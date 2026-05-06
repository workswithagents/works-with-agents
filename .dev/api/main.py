#!/usr/bin/env python3.11
"""
Works With Agents — Knowledge Platform API
All knowledge: FactBase, Skill Registry, Pitfall Registry.

Endpoints:
  GET  /v1/health                       — API health check
  GET  /v1/version                      — version hash for on-prem sync
  GET  /v1/facts?entity=X&category=Y    — query facts (limit=200 default, max 10000)
  POST /v1/facts                        — set a fact (upsert)
  GET  /v1/facts/stats                  — factbase stats
  GET  /v1/skills/{name}                — skill metadata + body
  GET  /v1/skills                       — list all skills
  POST /v1/pitfalls                     — report a bug (shared knowledge)
  GET  /v1/pitfalls                     — query pitfall registry (limit=100 default)
  GET  /v1/auth/{service}               — credential lookup
  POST /v1/newsletter/subscribe         — newsletter signup

On-prem: Docker image available. Set SYNC_FROM=https://workswithagents.dev for periodic sync.

Ops/monitoring (heartbeat, fleet health) → bastiongateway.com.
Blueprint Registry (verified LLM configs) → workswithagents.io.
"""

import hashlib, json, os, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Works With Agents — Knowledge Platform", version="0.3.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_DIR = Path(os.environ.get("FACTBASE_DIR", Path(__file__).resolve().parent / "data"))
DB_DIR.mkdir(parents=True, exist_ok=True)
FACTS_DB = DB_DIR / "facts.db"
PITFALLS_DB = DB_DIR / "pitfalls.db"

@contextmanager
def _facts_conn():
    conn = sqlite3.connect(str(FACTS_DB)); conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA busy_timeout=5000")
    try: yield conn
    finally: conn.close()

@contextmanager
def _pitfalls_conn():
    conn = sqlite3.connect(str(PITFALLS_DB)); conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try: yield conn
    finally: conn.close()

def _init():
    with _facts_conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY AUTOINCREMENT, entity TEXT NOT NULL, attribute TEXT NOT NULL, value TEXT NOT NULL, category TEXT NOT NULL, source TEXT DEFAULT 'agent', verified INTEGER DEFAULT 0, note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now')));
            CREATE UNIQUE INDEX IF NOT EXISTS idx_fact_unique ON facts(entity, attribute);
            CREATE INDEX IF NOT EXISTS idx_fact_category ON facts(category);
            CREATE TABLE IF NOT EXISTS newsletter_subs (email TEXT PRIMARY KEY, subscribed_at TEXT NOT NULL, confirmed INTEGER DEFAULT 0);
        """)
        c.commit()
    with _pitfalls_conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS pitfalls_log (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL, tool TEXT NOT NULL, error TEXT NOT NULL, fix TEXT DEFAULT '', session_id TEXT, logged_at TEXT NOT NULL DEFAULT (datetime('now')));
            CREATE INDEX IF NOT EXISTS idx_pitfalls_tool ON pitfalls_log(tool);
        """)
        c.commit()

_init()

# ── Models ───────────────────────────────────────────────────────────
class FactSet(BaseModel):
    entity: str; attribute: str; value: str; category: str = "reference"
    source: str = "agent"; verified: int = 0; note: str = ""

class PitfallReport(BaseModel): agent_id: str; tool: str; error: str; fix: str = ""; session_id: Optional[str] = None
class NewsletterSub(BaseModel): email: str

# ── FactBase ─────────────────────────────────────────────────────────
@app.get("/v1/facts")
def get_facts(entity: Optional[str]=Query(None), category: Optional[str]=Query(None), attribute: Optional[str]=Query(None), keyword: Optional[str]=Query(None), limit: Optional[int]=Query(200)):
    q = "SELECT * FROM facts WHERE 1=1"; p = []
    if entity: q += " AND entity = ?"; p.append(entity)
    if category: q += " AND category = ?"; p.append(category)
    if attribute: q += " AND attribute = ?"; p.append(attribute)
    if keyword: q += " AND (entity LIKE ? OR attribute LIKE ? OR value LIKE ?)"; like = f"%{keyword}%"; p.extend([like,like,like])
    q += f" ORDER BY category, entity, attribute LIMIT {min(limit, 10000)}"
    with _facts_conn() as c: rows = c.execute(q, p).fetchall()
    return {"facts": [dict(r) for r in rows], "count": len(rows)}

@app.post("/v1/facts")
def set_fact(fact: FactSet):
    now = datetime.now(timezone.utc).isoformat()
    with _facts_conn() as c:
        ex = c.execute("SELECT id FROM facts WHERE entity=? AND attribute=?", (fact.entity, fact.attribute)).fetchone()
        if ex: c.execute("UPDATE facts SET value=?,category=?,source=?,verified=?,note=?,updated_at=? WHERE entity=? AND attribute=?", (fact.value,fact.category,fact.source,fact.verified,fact.note,now,fact.entity,fact.attribute))
        else: c.execute("INSERT INTO facts (entity,attribute,value,category,source,verified,note,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (fact.entity,fact.attribute,fact.value,fact.category,fact.source,fact.verified,fact.note,now,now))
        c.commit()
    return {"status":"ok","entity":fact.entity,"attribute":fact.attribute}

@app.get("/v1/facts/stats")
def facts_stats():
    with _facts_conn() as c:
        total = c.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        cats = c.execute("SELECT category, COUNT(*) as cnt FROM facts GROUP BY category ORDER BY cnt DESC").fetchall()
    return {"total_facts": total, "by_category": {r["category"]:r["cnt"] for r in cats}}

# ── Skills Registry ──────────────────────────────────────────────────
SKILLS_DIR = Path(os.environ.get("SKILLS_DIR", os.path.expanduser("~/.hermes/skills")))

@app.get("/v1/skills")
def list_skills():
    skills = []
    if SKILLS_DIR.exists():
        for sm in sorted(SKILLS_DIR.rglob("SKILL.md")):
            rel = sm.relative_to(SKILLS_DIR); cat = rel.parts[0] if len(rel.parts)>1 else "root"
            skills.append({"name":sm.parent.name,"category":cat,"path":str(rel)})
    return {"skills":skills,"count":len(skills)}

@app.get("/v1/skills/{name}")
def get_skill(name:str):
    for sm in SKILLS_DIR.rglob("SKILL.md"):
        if sm.parent.name == name:
            content = sm.read_text(); fm = {}
            if content.startswith("---"):
                parts = content.split("---",2)
                if len(parts)>=3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line: k,v = line.split(":",1); fm[k.strip()]=v.strip()
            return {"name":name,"path":str(sm.relative_to(SKILLS_DIR)),"frontmatter":fm,"size":len(content),"body":content}
    raise HTTPException(404, f"Skill '{name}' not found")

# ── Pitfall Registry (Knowledge) ────────────────────────────────────
@app.get("/v1/pitfalls")
def get_pitfalls(tool: Optional[str]=Query(None), keyword: Optional[str]=Query(None), limit: Optional[int]=Query(100)):
    q = "SELECT * FROM pitfalls_log WHERE 1=1"; p = []
    if tool: q += " AND tool = ?"; p.append(tool)
    if keyword: q += " AND (tool LIKE ? OR error LIKE ? OR fix LIKE ?)"; like=f"%{keyword}%"; p.extend([like,like,like])
    q += f" ORDER BY logged_at DESC LIMIT {min(limit, 10000)}"
    with _pitfalls_conn() as c: rows = c.execute(q,p).fetchall()
    return {"pitfalls":[dict(r) for r in rows],"count":len(rows)}

@app.post("/v1/pitfalls")
def report_pitfall(pit: PitfallReport):
    now = datetime.now(timezone.utc).isoformat()
    with _pitfalls_conn() as c:
        c.execute("INSERT INTO pitfalls_log (agent_id,tool,error,fix,session_id,logged_at) VALUES (?,?,?,?,?,?)", (pit.agent_id, pit.tool, pit.error, pit.fix, pit.session_id, now))
        c.commit()
    return {"status":"ok","agent_id":pit.agent_id,"tool":pit.tool}

# ── Auth ─────────────────────────────────────────────────────────────
@app.get("/v1/auth/{service}")
def auth_lookup(service:str):
    with _facts_conn() as c: rows = c.execute("SELECT * FROM facts WHERE entity = ? AND category = 'auth'", (service,)).fetchall()
    if not rows: raise HTTPException(404, f"No auth facts for '{service}'")
    return {"service":service,"facts":[dict(r) for r in rows]}

# ── Newsletter ──────────────────────────────────────────────────────
@app.post("/v1/newsletter/subscribe")
def newsletter_subscribe(sub:NewsletterSub):
    now = datetime.now(timezone.utc).isoformat()
    with _facts_conn() as c:
        if c.execute("SELECT 1 FROM newsletter_subs WHERE email = ?",(sub.email,)).fetchone():
            return {"message":"Already subscribed!","email":sub.email}
        c.execute("INSERT INTO newsletter_subs (email,subscribed_at) VALUES (?,?)",(sub.email,now)); c.commit()
    return {"message":"Subscribed!","email":sub.email}

# ── Health ───────────────────────────────────────────────────────────
@app.get("/v1/health")
def health(): return {"status":"ok","version":app.version,"timestamp":datetime.now(timezone.utc).isoformat()}

@app.get("/v1/version")
def get_version():
    """Version hash for on-prem sync. Computed from all facts, pitfalls, and skills."""
    h = hashlib.sha256()
    with _facts_conn() as c:
        rows = c.execute("SELECT entity, attribute, value, updated_at FROM facts ORDER BY id").fetchall()
        for r in rows:
            h.update(f"{r['entity']}|{r['attribute']}|{r['value']}|{r['updated_at']}".encode())
    with _pitfalls_conn() as c:
        rows = c.execute("SELECT id, tool, error, fix, logged_at FROM pitfalls_log ORDER BY id").fetchall()
        for r in rows:
            h.update(f"{r['id']}|{r['tool']}|{r['error']}|{r['fix']}|{r['logged_at']}".encode())
    if SKILLS_DIR.exists():
        for sm in sorted(SKILLS_DIR.rglob("SKILL.md")):
            content = sm.read_text()
            h.update(f"{sm}|{sm.stat().st_mtime}".encode())
    return {"version":h.hexdigest(),"updated":datetime.now(timezone.utc).isoformat()}

# ── Home ─────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Works With Agents — Knowledge Platform</title>
<style>
  :root{--bg:#f8fafc;--card:#fff;--text:#0f172a;--muted:#475569;--accent:#059669;--cta:#D97706;--border:#e2e8f0;--code-bg:#f1f5f9;--shadow:0 1px 3px rgba(0,0,0,0.06)}
  @media(prefers-color-scheme:dark){:root{--bg:#0f172a;--card:#1e293b;--text:#f1f5f9;--muted:#94a3b8;--accent:#10B981;--cta:#F59E0B;--border:#334155;--code-bg:#0f172a}}
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}
  .container{max-width:800px;margin:0 auto;padding:40px 24px}
  nav{display:flex;justify-content:space-between;align-items:center;padding-bottom:16px;border-bottom:1px solid var(--border);margin-bottom:32px}
  .logo{font-size:16px;font-weight:700;color:var(--text);text-decoration:none}.logo span{color:var(--accent)}
  .nav-links{display:flex;gap:20px}.nav-links a{color:var(--muted);text-decoration:none;font-size:13px;font-weight:500}.nav-links a:hover{color:var(--text)}
  h1{font-size:28px;font-weight:800;letter-spacing:-.3px;margin-bottom:6px}h1 .t{color:var(--accent)}
  .badge{display:inline-block;padding:3px 12px;background:color-mix(in srgb,var(--accent) 10%,transparent);color:var(--accent);border-radius:20px;font-size:12px;font-weight:600;margin-bottom:20px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:22px;margin-bottom:14px;box-shadow:var(--shadow)}.card h2{font-size:15px;margin-bottom:10px;font-weight:700}
  .endpoint{font-family:'SF Mono',SFMono-Regular,Consolas,monospace;background:var(--code-bg);padding:6px 10px;border-radius:6px;margin:5px 0;font-size:12px;border-left:3px solid var(--accent)}
  .method{font-weight:700;color:var(--cta)}.path{color:var(--text)}
  a{color:var(--accent);text-decoration:none;font-weight:500}a:hover{text-decoration:underline}
  .tag{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600;margin-left:8px}.tag-knowledge{background:color-mix(in srgb,var(--accent) 15%,transparent);color:var(--accent)}.tag-ops{background:color-mix(in srgb,var(--cta) 15%,transparent);color:var(--cta)}
  footer{text-align:center;padding:24px 0 0;border-top:1px solid var(--border);margin-top:24px;color:var(--muted);font-size:13px}footer a{color:var(--accent)}
</style>
<body><div class="container">
<nav>
  <a href="/" class="logo">Works <span>With</span> Agents</a>
  <div class="nav-links">
    <a href="https://workswithagents.com">Education</a>
    <a href="https://workswithagents.com/about.html">About</a>
    <a href="https://workswithagents.co.uk">UK</a>
    <a href="https://bastiongateway.com">Bastion</a>
  </div>
</nav>

  <div class="badge">Knowledge platform — live on HTTPS</div>
  <h1>Knowledge <span class="t">Platform</span></h1>
  <p style="color:var(--muted);font-size:14px;margin-bottom:24px">Source of truth for AI agent facts, skills, and shared knowledge.</p>

  <div class="card"><h2>FactBase</h2>
    <div class="endpoint"><span class="method">GET</span> <span class="path">/v1/facts?entity=python&category=env</span></div>
    <div class="endpoint"><span class="method">POST</span> <span class="path">/v1/facts</span></div>
    <div class="endpoint"><span class="method">GET</span> <span class="path">/v1/facts/stats</span></div>
  </div>

  <div class="card"><h2>Skill Registry</h2>
    <div class="endpoint"><span class="method">GET</span> <span class="path">/v1/skills</span></div>
    <div class="endpoint"><span class="method">GET</span> <span class="path">/v1/skills/{name}</span></div>
  </div>

  <div class="card"><h2>Pitfall Registry</h2>
    <div class="endpoint"><span class="method">GET</span> <span class="path">/v1/pitfalls?tool=spfx</span></div>
    <div class="endpoint"><span class="method">POST</span> <span class="path">/v1/pitfalls</span></div>
    <p style="font-size:12px;color:var(--muted);margin-top:8px">Bugs found by one agent, learned by all.</p>
  </div>

  <div class="card"><h2>Blueprint Registry</h2>
    <p style="font-size:13px;color:var(--muted);margin-bottom:4px">Verified LLM configurations, hardware-matched → <a href="https://workswithagents.io">workswithagents.io</a></p>
  </div>

  <div class="card"><h2>Ops & Monitoring</h2>
    <p style="font-size:13px;color:var(--muted);margin-bottom:4px">Heartbeat, fleet health, and agent monitoring → <a href="https://bastiongateway.com">bastiongateway.com</a></p>
  </div>

  <div class="card"><h2>Docs</h2>
    <p style="font-size:13px;margin-bottom:5px"><a href="/llms.txt">llms.txt</a> — AI agent documentation index</p>
    <p style="font-size:13px;margin-bottom:5px"><a href="/llms-full.txt">llms-full.txt</a> — Full docs in one file</p>
    <p style="font-size:13px;margin-bottom:5px"><a href="/v1/openapi.json">openapi.json</a> — OpenAPI 3.1 spec</p>
    <p style="font-size:13px"><a href="/docs">/docs</a> — Swagger UI</p>
  </div>

  <div class="card">
    <h2>🖥 On-Prem Knowledge Platform</h2>
    <p style="font-size:13px;color:var(--muted);margin-bottom:12px">Run your own knowledge platform behind the firewall. Syncs facts, skills, and pitfalls from the public registry — your internal agents query local, stay air-gapped.</p>
    <div class="endpoint" style="margin-bottom:6px;overflow-x:auto;white-space:pre;font-size:11px">docker pull workswithagents/knowledge-platform:latest
docker run -p 8499:8499 \\
  -v ./data:/app/data \\
  -v ./skills:/app/skills \\
  -e SYNC_FROM=https://workswithagents.dev \\
  workswithagents/knowledge-platform</div>
    <p style="font-size:12px;color:var(--muted);margin-top:8px">Enterprise support available. <a href="mailto:enterprise@workswithagents.com">Contact us →</a></p>
  </div>

  <footer>
    <p>Works With Agents · <a href="https://workswithagents.com">Education</a> · <a href="https://workswithagents.com/about.html">About</a> · © 2026</p>
  </footer>
</div></body></html>"""

# ── Static Docs ──────────────────────────────────────────────────────
DOCS_DIR = Path(__file__).resolve().parent.parent

@app.get("/llms.txt", response_class=HTMLResponse)
@app.get("/llms-full.txt", response_class=HTMLResponse)
async def serve_llms_txt(request: Request):
    from fastapi.responses import PlainTextResponse
    fp = DOCS_DIR / request.url.path.lstrip("/")
    return PlainTextResponse(fp.read_text(), media_type="text/plain; charset=utf-8") if fp.exists() else HTTPException(404)

@app.get("/v1/openapi.json")
def serve_openapi():
    sp = DOCS_DIR / "openapi.json"
    return JSONResponse(json.loads(sp.read_text())) if sp.exists() else HTTPException(404)
