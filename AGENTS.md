# AGENTS.md — Works With Agents (workspace root)

Multi-domain platform for AI agent infrastructure, education, and consulting.
Co-founded by Vilius Vystartas (technical) & Pelin Kayhan (business/compliance).

## Domains

| Domain | Purpose | Tech | Deploy |
|---|---|---|---|
| workswithagents.dev | Agent API — facts, skills, fleet health | FastAPI (Worker) | `npx wrangler deploy` |
| workswithagents.com | Global education — courses, newsletter | Static HTML (Pages) | `npx wrangler pages deploy` |
| workswithagents.co.uk | UK education mirror | Static HTML (Pages) | `npx wrangler pages deploy` |
| bastiongateway.com | Infrastructure — license, proxy, admin | FastAPI (Worker) | `npx wrangler deploy` |

## Key files

- `deploy.sh` — deploy all 4 domains
- `.dev/api/main.py` — Agent Operations API (FastAPI, all endpoints live)
- `.dev/llms.txt` / `.dev/llms-full.txt` — AI agent documentation index
- `.dev/openapi.json` — OpenAPI 3.1 spec
- `.dev/decisions.md` — Architecture decisions (theme, i18n, security, GDPR)
- `.com/index.html` — Global education landing page
- `.com/llms.txt` / `.com/llms-full.txt` — Education docs for AI agents
- `.co.uk/index.html` — UK education landing page
- `.co.uk/llms.txt` / `.co.uk/llms-full.txt` — UK education docs for AI agents
- `~/Agent-Projects/bastion-gateway/api/main.py` — Bastion Gateway

## Agent discovery

```
curl https://workswithagents.dev/llms.txt        → Documentation index
curl https://workswithagents.dev/llms-full.txt   → Full docs (one file)
curl https://workswithagents.dev/v1/openapi.json → API contract
```

## Build order

1. ✅ FactBase CLI + client
2. ✅ .dev API (facts, skills, heartbeat, fleet health, pitfalls, newsletter)
3. ✅ Landing pages (.com, .co.uk)
4. ✅ Bastion Gateway (license, proxy, admin)
5. ✅ llms.txt / llms-full.txt / openapi.json on all 3 domains
6. 🔜 Cloudflare deployment (DNS + D1 databases needed)
7. 🔜 Newsletter integration (ConvertKit/Buttondown)
8. 🔜 Course platform integration
