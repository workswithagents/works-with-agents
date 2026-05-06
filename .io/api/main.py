#!/usr/bin/env python3.11
"""
workswithagents.io — Blueprint Registry
Verified LLM configurations, hardware-matched. Agent-submitted, human-browsable.

Endpoints:
  GET  /v1/blueprints                  — list all blueprints
  GET  /v1/blueprints/{id}             — single blueprint
  POST /v1/blueprints/match            — match system specs to blueprints
  POST /v1/blueprints/submit           — agent-submitted blueprint
  GET  /v1/blueprints/version          — registry version (for caching)
  GET  /v1/health                      — health check
  GET  /llms.txt                       — agent discovery
"""

import hashlib, json, os, uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel

app = FastAPI(
    title="Works With Agents — Blueprint Registry",
    version="0.3.0",
    docs_url="/docs"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).resolve().parent.parent
BLUEPRINTS_DIR = Path(os.environ.get("BLUEPRINTS_DIR", BASE_DIR / "blueprints"))
BLUEPRINTS_SUBMITTED = BLUEPRINTS_DIR / "submitted"
DOCS_DIR = BASE_DIR

# ── Version tracking ──────────────────────────────────────────────────

def _registry_version() -> str:
    """Compute a stable version hash from all blueprint files. Changes when any file changes."""
    hasher = hashlib.sha256()
    if BLUEPRINTS_DIR.exists():
        for f in sorted(BLUEPRINTS_DIR.glob("*.md")):
            hasher.update(f.name.encode())
            hasher.update(str(f.stat().st_mtime).encode())
    return hasher.hexdigest()[:16]


def _registry_mtime() -> str:
    """ISO timestamp of most recent blueprint change."""
    mtime = 0.0
    if BLUEPRINTS_DIR.exists():
        for f in BLUEPRINTS_DIR.glob("*.md"):
            mtime = max(mtime, f.stat().st_mtime)
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat() if mtime else ""


# ── Blueprint parsing ─────────────────────────────────────────────────

try:
    import yaml as _yaml

    def _parse_blueprint(path: Path) -> dict | None:
        text = path.read_text()
        if not text.startswith("---"): return None
        parts = text.split("---", 2)
        if len(parts) < 3: return None
        fm = _yaml.safe_load(parts[1]) or {}
        fm["body"] = parts[2].strip()
        fm["id"] = fm.get("id") or path.stem
        return fm

    def _parse_blueprint_content(content: str) -> dict | None:
        if not content.startswith("---"): return None
        parts = content.split("---", 2)
        if len(parts) < 3: return None
        return _yaml.safe_load(parts[1]) or {}
except ImportError:
    import re as _re

    def _parse_yaml_value(v: str):
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            if not inner: return []
            return [x.strip().strip('"').strip("'") for x in inner.split(",")]
        if v.lower() in ("true", "false"): return v.lower() == "true"
        if v.isdigit(): return int(v)
        try: return float(v)
        except: pass
        return v.strip('"').strip("'")

    def _parse_blueprint(path: Path) -> dict | None:
        text = path.read_text()
        if not text.startswith("---"): return None
        parts = text.split("---", 2)
        if len(parts) < 3: return None
        fm = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = _parse_yaml_value(v)
        fm["body"] = parts[2].strip()
        fm["id"] = fm.get("id") or path.stem
        return fm

    def _parse_blueprint_content(content: str) -> dict | None:
        if not content.startswith("---"): return None
        parts = content.split("---", 2)
        if len(parts) < 3: return None
        fm = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        return fm


def _load_blueprints(verified_only: bool = True) -> list[dict]:
    if not BLUEPRINTS_DIR.exists(): return []
    blueprints = []
    for f in sorted(BLUEPRINTS_DIR.glob("*.md")):
        r = _parse_blueprint(f)
        if r and (not verified_only or r.get("verified")):
            blueprints.append(r)
    return blueprints


# ── Matching ──────────────────────────────────────────────────────────

def _match_fit(blueprint: dict, os_name: str, ram: int, gpu: str | None) -> str | None:
    if os_name not in blueprint.get("os", []): return None
    gpu_list = blueprint.get("gpu", [])
    gpu_match = not gpu or any(gpu.startswith(g) or g.startswith(gpu) for g in gpu_list)
    rec_ram = blueprint.get("recommended_ram_gb", 999)
    min_ram = blueprint.get("min_ram_gb", 0)
    if gpu_match and ram >= rec_ram: return "optimal"
    if gpu_match and ram >= min_ram: return "compatible"
    if gpu_match and ram < min_ram: return "insufficient_ram"
    if os_name in blueprint.get("os", []): return "minimal"
    return None


def _make_match(r: dict, fit: str) -> dict:
    return {
        "id": r.get("id", ""), "name": r.get("name", ""), "fit": fit,
        "model": r.get("model", ""), "model_family": r.get("model_family", ""),
        "model_size_b": r.get("model_size_b", 0), "harness": r.get("harness", ""),
        "min_ram_gb": r.get("min_ram_gb", 0), "recommended_ram_gb": r.get("recommended_ram_gb", 0),
        "min_disk_gb": r.get("min_disk_gb", 0), "gpu": r.get("gpu", []),
        "context_length": r.get("context_length", 0), "quantization": r.get("quantization", ""),
        "available_sizes": r.get("available_sizes", []), "skills": r.get("skills", []),
        "pitfalls": r.get("pitfalls", []), "setup_script": r.get("setup_script", ""),
        "config_snippet": r.get("config_snippet", ""), "tokens_per_sec": r.get("tokens_per_sec", ""),
    }


def _suggest(blueprints: list[dict], os_name: str, ram: int, gpu: str | None) -> dict:
    """Suggest upgrades and downgrades across families."""
    upgrades, downgrades = [], []
    families_seen = set()
    for r in blueprints:
        fid = (r.get("model_family"), r.get("harness"))
        if fid in families_seen: continue
        families_seen.add(fid)
        sizes = r.get("available_sizes", [])
        current = r.get("model_size_b", 0)
        gpu_ok = not gpu or any(gpu.startswith(g) or g.startswith(gpu) for g in r.get("gpu", []))
        if not gpu_ok: continue
        for s in sorted(sizes):
            if s > current and s <= ram * 0.5:
                upgrades.append({
                    "blueprint_id": f"{r.get('harness','')}-{r.get('model_family','').lower()}{int(s)}b" if s == int(s) else f"{r.get('harness','')}-{r.get('model_family','').lower()}{s}b",
                    "size_b": s, "family": r.get("model_family"),
                    "reason": f"Your {ram}GB RAM can handle {s}B models"
                })
        for s in sorted(sizes, reverse=True):
            if s < current:
                est_ram = max(s * 2, 8)
                if ram >= est_ram:
                    downgrades.append({
                        "blueprint_id": f"{r.get('harness','')}-{r.get('model_family','').lower()}{int(s)}b" if s == int(s) else f"{r.get('harness','')}-{r.get('model_family','').lower()}{s}b",
                        "size_b": s, "family": r.get("model_family"),
                        "reason": f"Fits your {ram}GB RAM (needs ~{est_ram}GB)"
                    })
                    break
    return {"upgrades": upgrades[:3], "downgrades": downgrades[:3]}


# ── Models ────────────────────────────────────────────────────────────

class BlueprintMatch(BaseModel):
    os: str = ""
    ram_gb: int = 0
    gpu: str | None = None
    disk_gb: int = 0


class BlueprintSubmit(BaseModel):
    content: str


# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/v1/health")
def health():
    return {
        "status": "ok",
        "version": app.version,
        "registry_version": _registry_version(),
        "registry_updated": _registry_mtime(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/v1/blueprints/version")
def blueprints_version():
    """Return current version for agent caching. Agents compare this to their stored version."""
    return {
        "version": _registry_version(),
        "updated": _registry_mtime(),
        "count": len(_load_blueprints())
    }


@app.get("/v1/blueprints")
def blueprints_list(request: Request):
    """List all verified blueprints. Returns ETag for caching."""
    blueprints = _load_blueprints()
    version = _registry_version()

    # Check If-None-Match for caching
    if_none = request.headers.get("If-None-Match", "")
    if if_none and if_none.strip('"') == version:
        return Response(status_code=304)

    body = {
        "blueprints": [{k: v for k, v in r.items() if k != "body"} for r in blueprints],
        "count": len(blueprints),
        "version": version,
        "updated": _registry_mtime()
    }
    return JSONResponse(
        content=body,
        headers={
            "ETag": f'"{version}"',
            "Cache-Control": "public, max-age=3600"
        }
    )


@app.get("/v1/blueprints/{name}")
def blueprints_get(name: str, request: Request):
    """Get a single blueprint by ID."""
    fp = BLUEPRINTS_DIR / f"{name}.md"
    if not fp.exists():
        raise HTTPException(404, f"Blueprint '{name}' not found")

    version = hashlib.md5(f"{name}{fp.stat().st_mtime}".encode()).hexdigest()[:16]
    if_none = request.headers.get("If-None-Match", "")
    if if_none and if_none.strip('"') == version:
        return Response(status_code=304)

    r = _parse_blueprint(fp)
    if not r: raise HTTPException(404)
    return JSONResponse(
        content=r,
        headers={
            "ETag": f'"{version}"',
            "Cache-Control": "public, max-age=3600"
        }
    )


@app.post("/v1/blueprints/match")
def blueprints_match(data: BlueprintMatch):
    """Match system specs to blueprints. Returns matches, insufficient, and upgrade/downgrade suggestions."""
    os_name = data.os
    ram = data.ram_gb
    gpu = data.gpu
    disk = data.disk_gb
    blueprints = _load_blueprints()
    matches, insufficient = [], []
    for r in blueprints:
        fit = _match_fit(r, os_name, ram, gpu)
        if fit == "insufficient_ram":
            insufficient.append(_make_match(r, fit))
        elif fit:
            if disk and disk < r.get("min_disk_gb", 0):
                r2 = _make_match(r, fit)
                r2["fit"] = "insufficient_disk"
                r2["disk_gap"] = r.get("min_disk_gb", 0) - disk
                insufficient.append(r2)
            else:
                matches.append(_make_match(r, fit))
    matches.sort(key=lambda m: {"optimal": 0, "compatible": 1, "minimal": 2}.get(m["fit"], 99))
    suggestions = _suggest(blueprints, os_name, ram, gpu)
    return {
        "matches": matches,
        "insufficient": insufficient,
        "suggestions": suggestions,
        "system": {"os": os_name, "ram_gb": ram, "gpu": gpu, "disk_gb": disk or None},
        "count": len(matches),
        "version": _registry_version()
    }


@app.post("/v1/blueprints/submit")
def blueprints_submit(data: BlueprintSubmit):
    """Agent-submitted blueprint for review."""
    content = data.content
    if not content or not content.startswith("---"):
        raise HTTPException(400, "Blueprint must start with YAML frontmatter (---)")
    BLUEPRINTS_SUBMITTED.mkdir(parents=True, exist_ok=True)
    r = _parse_blueprint_content(content)
    rid = (r or {}).get("id") if r else None
    if not rid:
        import uuid
        rid = uuid.uuid4().hex[:8]
    fp = BLUEPRINTS_SUBMITTED / f"{rid}.md"
    fp.write_text(content)
    return {"status": "submitted", "id": rid, "message": "Thanks! Blueprint submitted for review."}


# ── llms.txt ──────────────────────────────────────────────────────────

@app.get("/llms.txt", response_class=PlainTextResponse)
@app.get("/llms-full.txt", response_class=PlainTextResponse)
async def serve_llms_txt(request: Request):
    fp = DOCS_DIR / request.url.path.lstrip("/")
    if fp.exists():
        return PlainTextResponse(fp.read_text(), media_type="text/plain; charset=utf-8")
    raise HTTPException(404)


# ── Landing page ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def landing():
    """Blueprint Registry landing — browse, match, submit."""
    version = _registry_version()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Blueprint Registry — Works With Agents</title>
<style>
  :root{{--bg:#f8fafc;--card:#fff;--text:#0f172a;--muted:#475569;--accent:#059669;--cta:#D97706;--border:#e2e8f0;--code-bg:#f1f5f9;--shadow:0 1px 3px rgba(0,0,0,0.06);--red:#ef4444;--optimal:#059669;--compatible:#D97706;--minimal:#f59e0b}}
  @media(prefers-color-scheme:dark){{:root{{--bg:#0f172a;--card:#1e293b;--text:#f1f5f9;--muted:#94a3b8;--accent:#10B981;--cta:#F59E0B;--border:#334155;--code-bg:#0f172a}}}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.7;-webkit-font-smoothing:antialiased}}
  .container{{max-width:880px;margin:0 auto;padding:0 24px}}
  nav{{display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:1px solid var(--border);margin-bottom:36px}}
  .logo{{font-size:16px;font-weight:700;color:var(--text);text-decoration:none}}.logo span{{color:var(--accent)}}
  .nav-links{{display:flex;gap:20px}}.nav-links a{{color:var(--muted);text-decoration:none;font-size:13px;font-weight:500}}.nav-links a:hover{{color:var(--text)}}
  .learn-dropdown{{position:relative;display:inline-block}}
  .learn-btn{{color:var(--accent);text-decoration:none;font-size:13px;font-weight:600}}
  .learn-btn:hover{{color:var(--text)}}
  .learn-menu{{display:none;position:absolute;top:100%;left:0;background:var(--card);border:1px solid var(--border);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.12);min-width:200px;z-index:50;padding:8px 0}}
  .learn-dropdown:hover .learn-menu{{display:block}}
  .learn-menu a{{display:block;padding:6px 16px;color:var(--muted);font-size:12px;text-decoration:none;white-space:nowrap}}
  .learn-menu a:hover{{background:var(--code-bg,var(--card));color:var(--text)}}
  .learn-menu .phase-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--accent);padding:8px 16px 4px;opacity:0.7}}
  .learn-menu .phase-label:first-child{{padding-top:4px}}
  h1{{font-size:32px;font-weight:800;letter-spacing:-.3px;margin-bottom:6px}}h1 span{{color:var(--accent)}}
  .subtitle{{font-size:15px;color:var(--muted);margin-bottom:28px}}
  .version-bar{{font-size:11px;color:var(--muted);margin-bottom:20px;padding:6px 12px;background:var(--code-bg);border-radius:6px;display:inline-block}}
  .filters{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:32px;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;box-shadow:var(--shadow)}}
  .filters label{{font-size:12px;color:var(--muted);font-weight:600;display:block;margin-bottom:4px}}
  .filters select,.filters input{{padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:13px;min-width:140px}}
  .filters button{{padding:8px 18px;background:var(--accent);color:#fff;border:none;border-radius:6px;font-weight:600;font-size:13px;cursor:pointer}}
  .blueprint{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:24px;margin-bottom:16px;box-shadow:var(--shadow)}}
  .blueprint h3{{font-size:17px;margin-bottom:4px}}.blueprint .meta{{font-size:13px;color:var(--muted);margin-bottom:10px}}
  .fit{{display:inline-block;padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;margin-left:8px}}
  .fit-optimal{{background:color-mix(in srgb,var(--optimal) 15%,transparent);color:var(--optimal)}}
  .fit-compatible{{background:color-mix(in srgb,var(--compatible) 15%,transparent);color:var(--compatible)}}
  .fit-minimal{{background:color-mix(in srgb,var(--minimal) 15%,transparent);color:var(--minimal)}}
  .fit-bad{{background:color-mix(in srgb,var(--red) 15%,transparent);color:var(--red)}}
  .blueprint .specs{{display:flex;gap:16px;flex-wrap:wrap;margin:10px 0;font-size:13px}}
  .blueprint .specs span{{padding:4px 10px;background:var(--code-bg);border-radius:4px;color:var(--muted)}}
  .blueprint pre{{background:var(--code-bg);padding:12px 16px;border-radius:6px;font-size:12px;overflow-x:auto;margin:10px 0;font-family:'SF Mono',SFMono-Regular,Consolas,monospace}}
  .blueprint .skills{{font-size:13px;color:var(--muted)}}.blueprint .skills a{{color:var(--accent)}}
  .suggestion{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin:6px 0;font-size:13px}}
  .suggestion strong{{color:var(--accent)}}
  .empty{{text-align:center;padding:60px 20px;color:var(--muted);font-size:15px}}
  .copy-instructions{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:24px;margin-top:40px;box-shadow:var(--shadow)}}
  .copy-instructions h2{{font-size:18px;margin-bottom:6px}}.copy-instructions p{{font-size:13px;color:var(--muted);margin-bottom:12px}}
  .copy-instructions pre{{background:var(--code-bg);padding:16px;border-radius:8px;font-size:12px;overflow-x:auto;font-family:'SF Mono',SFMono-Regular,Consolas,monospace;line-height:1.6;border:1px solid var(--border)}}
  .copy-instructions button{{margin-top:10px;padding:8px 18px;background:var(--accent);color:#fff;border:none;border-radius:6px;font-weight:600;font-size:13px;cursor:pointer}}
  .copy-instructions .copied{{display:inline-block;margin-left:10px;font-size:12px;color:var(--accent);opacity:0;transition:opacity .2s}}.copy-instructions .copied.show{{opacity:1}}
  .docker-section{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:24px;margin-top:40px;box-shadow:var(--shadow)}}
  .docker-section h2{{font-size:18px;margin-bottom:6px}}.docker-section p{{font-size:13px;color:var(--muted);margin-bottom:12px}}
  app-footer{{text-align:center;padding:40px 0;border-top:1px solid var(--border);margin-top:40px;color:var(--muted);font-size:13px}}app-footer a{{color:var(--accent);text-decoration:none}}
  .sites-dropdown{{position:relative;display:inline-block}}.sites-btn{{color:var(--muted);text-decoration:none;font-size:13px;font-weight:500;cursor:pointer}}.sites-btn:hover{{color:var(--text)}}.sites-menu{{display:none;position:absolute;top:100%;right:0;background:var(--card);border:1px solid var(--border);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.12);min-width:180px;z-index:50;padding:8px 0}}.sites-dropdown:hover .sites-menu{{display:block}}.sites-menu a{{display:block;padding:6px 16px;color:var(--muted);font-size:12px;text-decoration:none;white-space:nowrap}}.sites-menu a:hover{{background:var(--code-bg,var(--card));color:var(--text)}}@media(max-width:640px){{.filters{{flex-direction:column}}nav{{flex-direction:column;gap:10px;margin-bottom:24px}}.nav-links{{flex-wrap:wrap;gap:12px;justify-content:center}}h1{{font-size:22px}}.container{{padding:0 12px}}}}
</style>
</head>
<body><div class="container">
<nav>
  <a href="/" class="logo">Works <span>With</span> Agents</a>
  <div class="nav-links">
    <div class="learn-dropdown">
      <a href="https://workswithagents.com/learn.html" class="learn-btn">Learn ▾</a>
      <div class="learn-menu">
        <span class="phase-label">Foundation</span>
        <a href="https://workswithagents.com/learn/boot.html">1. Boot</a>
        <a href="https://workswithagents.com/learn/skills.html">2. Skills</a>
        <a href="https://workswithagents.com/learn/memory.html">3. Memory</a>
        <span class="phase-label">Autonomy</span>
        <a href="https://workswithagents.com/learn/decision-protocols.html">4. Decision Protocols</a>
        <a href="https://workswithagents.com/learn/tool-composition.html">5. Tool Composition</a>
        <span class="phase-label">Scale</span>
        <a href="https://workswithagents.com/learn/orchestration.html">6. Orchestration</a>
        <a href="https://workswithagents.com/learn/pipelines.html">7. Pipelines</a>
        <span class="phase-label">Harden</span>
        <a href="https://workswithagents.com/learn/resilience.html">8. Resilience</a>
        <a href="https://workswithagents.com/learn/verify.html">9. Verify</a>
        <a href="https://workswithagents.com/learn/compounding.html">10. Compounding</a>
      </div>
    </div>
    <a href="https://workswithagents.com/standards.html">Standards</a>\n    <a href="https://workswithagents.com/blog.html">Blog</a>
    <a href="https://workswithagents.com/about.html">About</a>
    <a href="https://workswithagents.com/contact.html">Contact</a>
    <a href="https://workswithagents.dev">Knowledge API</a>
    <a href="https://workswithagents.co.uk">UK</a>
    <a href="https://bastiongateway.com">Bastion</a>
    <div class="sites-dropdown">
      <a class="sites-btn">Sites ▾</a>
      <div class="sites-menu">
        <a href="https://workswithagents.com">Education</a>
        <a href="https://workswithagents.dev">Knowledge API</a>
        <a href="https://workswithagents.co.uk">UK</a>
        <a href="https://bastiongateway.com">Bastion</a>
      </div>
    </div>
  </div>
</nav>

<h1>Blueprint <span>Registry</span></h1>
<p class="subtitle">Verified LLM configurations, hardware-matched. Agents submit — agents discover.</p>
<p class="version-bar">🔖 Registry v{version} · {_registry_mtime()[:16] or 'initial'}</p>

<div class="filters">
  <div><label>OS</label><select id="f-os"><option value="">Any</option><option value="macOS">macOS</option><option value="Linux">Linux</option></select></div>
  <div><label>GPU</label><select id="f-gpu"><option value="">Any</option><option value="M1">M1</option><option value="M2">M2</option><option value="M3">M3</option><option value="M4">M4</option><option value="NVIDIA">NVIDIA</option></select></div>
  <div><label>RAM (GB)</label><input type="number" id="f-ram" placeholder="Any" min="0" style="width:100px"></div>
  <div style="display:flex;align-items:flex-end"><button onclick="filter()">Find Blueprint</button></div>
</div>
<div id="suggestions"></div>
<div id="blueprints"></div>
<div id="empty" class="empty" style="display:none"><p>No blueprints match your system. <a href="#agent-submit">Submit one via your agent →</a></p></div>

<div class="copy-instructions" id="agent-submit">
  <h2>🤖 Submit a Blueprint via Your Agent</h2>
  <p>Blueprints are submitted by AI agents — not humans. Copy the instructions below, paste into your agent, and let it handle the rest.</p>
  <pre id="agent-prompt">To submit a verified LLM blueprint to the Works With Agents registry:

1. Check the registry at https://workswithagents.io/llms.txt for schema and API docs
2. GET https://workswithagents.io/v1/blueprints to see existing blueprints — don't duplicate
3. Create a markdown file with YAML frontmatter matching the schema
4. POST the full markdown to https://workswithagents.io/v1/blueprints/submit
5. The blueprint will be reviewed and merged once hardware-verified

Schema: id, name, model, model_family, model_size_b, harness, os[], gpu[], min_ram_gb, recommended_ram_gb, min_disk_gb, context_length, quantization, available_sizes[], skills[], pitfalls[], setup_script, config_snippet, tokens_per_sec, verified_by, verified_date, verified_system, verified: true</pre>
  <button onclick="copyAgentPrompt()">📋 Copy Instructions</button>
  <span id="copied-msg" class="copied">Copied!</span>
</div>

<div class="docker-section">
  <h2>🖥 On-Prem Registry</h2>
  <p>Run your own blueprint registry behind the firewall. Docker image syncs with the public registry — your internal agents match against your verified configurations.</p>
  <pre>docker pull workswithagents/blueprint-registry:latest
docker run -p 8200:8200 \\
  -v ./blueprints:/blueprints \\
  -e SYNC_FROM=https://workswithagents.io \\
  workswithagents/blueprint-registry</pre>
  <p style="font-size:12px;color:var(--muted);margin-top:8px">Enterprise support available. <a href="mailto:enterprise@workswithagents.com">Contact us →</a></p>
</div>

<app-footer><p>Works With Agents · <a href="https://workswithagents.com">Education</a> · <a href="https://workswithagents.dev">Knowledge API</a> · <a href="https://workswithagents.com/about.html">About</a> · © 2026</p></app-footer>
</div>

<script>
const BLUEPRINTS = [{{
  id:"omlx-qwen8b",name:"oMLX + Qwen 2.5 8B",model:"Qwen2.5-8B-oQ4",model_family:"Qwen",model_size_b:8,harness:"oMLX",
  os:["macOS"],gpu:["M1","M2","M3","M4"],min_ram_gb:16,recommended_ram_gb:32,min_disk_gb:8,
  context_length:128000,quantization:"Q4_K_M",available_sizes:[1.5,3,7,8,14,32],
  skills:["agentic-delegation","spfx-local","hermes-agent"],
  pitfalls:["context_window below 64K — set context_length:128000","Python 3.9 crashes — use python3.11","delegation needs context_length too"],
  setup_script:"pip3.11 install omlx\\nomlx pull Qwen2.5-8B-oQ4\\nomlx serve --model Qwen2.5-8B-oQ4 --port 8000",
  config_snippet:"providers:\\n  omlx:\\n    api: http://127.0.0.1:8000/v1\\n    default_model: Qwen2.5-8B-oQ4\\n    models:\\n      Qwen2.5-8B-oQ4:\\n        context_length: 128000\\ndelegation:\\n  model: Qwen2.5-8B-oQ4\\n  provider: omlx\\n  context_length: 128000",
  tokens_per_sec:"~20 (M4/24GB), ~15 (M2/16GB)",verified_by:"Vilius Vystartas",verified_date:"2026-05-05"
}}];

function matchFit(r,os,gpu,ram,disk){{
  if(os && !r.os.includes(os)) return null;
  const gm = !gpu || r.gpu.some(g=>g.startsWith(gpu)||gpu.startsWith(g));
  if(!gm && gpu) return null;
  if(disk && disk < r.min_disk_gb) return "insufficient_disk";
  if(ram && ram >= r.recommended_ram_gb) return "optimal";
  if(ram && ram >= r.min_ram_gb) return "compatible";
  if(ram && ram < r.min_ram_gb) return "insufficient_ram";
  return gm?"compatible":null;
}}

function suggest(os,gpu,ram){{
  const el = document.getElementById('suggestions');
  const upgrades=[],downgrades=[];
  if(!ram) return el.innerHTML='';
  BLUEPRINTS.forEach(r=>{{
    if(os && !r.os.includes(os)) return;
    if(gpu && !r.gpu.some(g=>g.startsWith(gpu))) return;
    r.available_sizes.filter(s=>s>r.model_size_b && s<=ram*0.5).forEach(s=>{{
      upgrades.push({{blueprint_id:`${{r.harness}}-${{r.model_family.toLowerCase()}}${{s}}b`,size_b:s,family:r.model_family,reason:"Your RAM can handle it"}});
    }});
    [...r.available_sizes].reverse().filter(s=>s<r.model_size_b).forEach(s=>{{
      const est = Math.max(s*2,8);
      if(ram >= est) downgrades.push({{blueprint_id:`${{r.harness}}-${{r.model_family.toLowerCase()}}${{s}}b`,size_b:s,family:r.model_family,reason:`Fits your ${{ram}}GB (needs ~${{est}}GB)`}});
    }});
  }});
  if(!upgrades.length && !downgrades.length) return el.innerHTML='';
  el.innerHTML = (upgrades.length?`<div style="margin-bottom:12px"><strong style="color:var(--accent)">↑ Upgrades your system can handle:</strong> ${{upgrades.slice(0,3).map(u=>`<span class="suggestion"><strong>${{u.blueprint_id}}</strong> (${{u.size_b}}B ${{u.family}}) — ${{u.reason}}</span>`).join('')}}</div>`:'')
    + (downgrades.length?`<div style="margin-bottom:20px"><strong style="color:var(--muted)">↓ Smaller alternatives:</strong> ${{downgrades.slice(0,3).map(d=>`<span class="suggestion"><strong>${{d.blueprint_id}}</strong> (${{d.size_b}}B ${{d.family}}) — ${{d.reason}}</span>`).join('')}}</div>`:'');
}}

function render(rs){{
  const el=document.getElementById('blueprints'),emp=document.getElementById('empty');
  if(!rs.length){{el.innerHTML='';emp.style.display='block';return}}
  emp.style.display='none';
  el.innerHTML=rs.map(r=>`<div class="blueprint">
    <h3>${{r.name}} <span class="fit fit-${{r._fit.startsWith('insufficient')?'bad':r._fit}}">${{r._fit}}</span></h3>
    <p class="meta">${{r.model_family}} family · ${{r.model_size_b}}B · ${{r.harness}} · Verified by ${{r.verified_by}} · ${{r.verified_date}}</p>
    <div class="specs">
      <span>🖥 ${{r.os.join(', ')}}</span><span>💾 ${{r.min_ram_gb}}–${{r.recommended_ram_gb}}GB RAM</span>
      <span>📀 ${{r.min_disk_gb}}GB disk</span><span>🎮 ${{r.gpu.join(', ')}}</span>
      <span>📦 ${{r.quantization}}</span><span>⚡ ${{r.tokens_per_sec}}</span>
    </div>
    <div class="specs"><span>Sizes: ${{r.available_sizes.map(s=>`${{s}}B`).join(', ')}}</span></div>
    ${{r._fit==='insufficient_ram'?`<p style="color:var(--red);font-size:14px;margin:10px 0">⚠ Needs ${{r.min_ram_gb}}GB+ RAM</p>`:''}}
    ${{r._fit==='insufficient_disk'?`<p style="color:var(--red);font-size:14px;margin:10px 0">⚠ Needs ${{r.min_disk_gb}}GB+ free disk</p>`:''}}
    <h4 style="font-size:14px;margin:12px 0 4px">Setup</h4><pre>${{r.setup_script}}</pre>
    <h4 style="font-size:14px;margin:12px 0 4px">Config</h4><pre>${{r.config_snippet}}</pre>
    <h4 style="font-size:14px;margin:12px 0 4px">Pitfalls</h4><ul style="font-size:13px;color:var(--muted);padding-left:20px">${{r.pitfalls.map(p=>`<li>${{p}}</li>`).join('')}}</ul>
    <p class="skills">Skills: ${{r.skills.map(s=>`<a href="https://workswithagents.dev/v1/skills/${{s}}">${{s}}</a>`).join(', ')}}</p>
    <p style="font-size:12px;color:var(--muted);margin-top:8px">Share: <code>workswithagents.io/blueprints/${{r.id}}.html</code></p>
  </div>`).join('');
}}

function filter(){{
  const os=document.getElementById('f-os').value,gpu=document.getElementById('f-gpu').value,ram=parseInt(document.getElementById('f-ram').value)||0;
  suggest(os,gpu,ram);
  const rs=BLUEPRINTS.map(r=>({{...r,_fit:matchFit(r,os,gpu,ram)}})).filter(r=>r._fit).sort((a,b)=>['optimal','compatible','minimal','insufficient_ram','insufficient_disk'].indexOf(a._fit)-['optimal','compatible','minimal','insufficient_ram','insufficient_disk'].indexOf(b._fit));
  render(rs);
}}
render(BLUEPRINTS.map(r=>({{...r,_fit:'compatible'}})));

function copyAgentPrompt(){{
  navigator.clipboard.writeText(document.getElementById('agent-prompt').textContent).then(()=>{{
    const msg = document.getElementById('copied-msg');
    msg.classList.add('show');
    setTimeout(()=>msg.classList.remove('show'),2000);
  }});
}}
</script>
</body></html>"""
