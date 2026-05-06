# AGENTS.md — Works With Agents

Agent infrastructure specifications and SDKs.
Co-founded by Vilius Vystartas (technical) & Pelin Kayhan (business/compliance).

## Portal

| Domain | Purpose | Tech | Deploy |
|---|---|---|---|
| workswithagents.dev | Sole public portal — API, specs, SDK docs | FastAPI (VPS) | Hetzner + nginx |
| workswithagents.com | 301 → workswithagents.dev | Static (Pages) | Cloudflare Pages |
| workswithagents.co.uk | 301 → workswithagents.dev | Static (Pages) | Cloudflare Pages |
| workswithagents.io | 301 → workswithagents.dev | nginx | Hetzner + nginx |
| bastiongateway.com | 301 → workswithagents.dev (admin at /admin) | FastAPI (VPS) | Hetzner + nginx |

## Key files

- `deploy.sh` — deploy static redirects (Cloudflare Pages) and API (VPS)
- `.dev/api/main.py` — Agent Operations API (FastAPI)
- `.dev/llms.txt` / `.dev/llms-full.txt` — AI agent documentation index
- `.dev/openapi.json` — OpenAPI 3.1 spec
- `.dev/specs/` — 15 protocol specifications (CC BY 4.0)
- `sdk/` — Python and TypeScript reference implementations
- `~/Agent-Projects/bastion-gateway/api/main.py` — Bastion Gateway (admin, license, fleet ops)

## Agent discovery

```
curl https://workswithagents.dev/llms.txt        → Documentation index
curl https://workswithagents.dev/llms-full.txt   → Full docs (one file)
curl https://workswithagents.dev/v1/openapi.json → API contract
```
