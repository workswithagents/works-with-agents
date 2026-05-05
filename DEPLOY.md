# Works With Agents — Deployment Runbook

## Prerequisites

- Cloudflare account with 4 DNS zones: workswithagents.dev, workswithagents.com, workswithagents.co.uk, bastiongateway.com
- `npx wrangler` authenticated (`npx wrangler login`)
- Node.js 22+ via fnm
- Python 3.11+ at /opt/homebrew/bin/python3.11

## Local Development

### .dev API
```bash
cd ~/Agent-Projects/works-with-agents/.dev
pip3.11 install fastapi uvicorn pydantic -q
python3.11 -m uvicorn api.main:app --reload --port 8499
# → http://localhost:8499/docs
```

### Bastion Gateway
```bash
cd ~/Agent-Projects/bastion-gateway
pip3.11 install fastapi uvicorn httpx pydantic -q
python3.11 -m uvicorn api.main:app --reload --port 8500
# → http://localhost:8500/docs
# Bootstrap admin token printed on first run
```

### Landing Pages (.com, .co.uk)
```bash
cd ~/Agent-Projects/works-with-agents
python3.11 -m http.server 8484 --directory .com
# → http://localhost:8484
```

## Production Deployment

### One-shot deploy all
```bash
chmod +x ~/Agent-Projects/works-with-agents/deploy.sh
~/Agent-Projects/works-with-agents/deploy.sh
```

### Per-domain deploy
```bash
# .dev (Worker)
cd ~/Agent-Projects/works-with-agents/.dev && npx wrangler deploy

# .com (Pages)
cd ~/Agent-Projects/works-with-agents/.com && npx wrangler pages deploy . --project-name workswithagents-com

# .co.uk (Pages)
cd ~/Agent-Projects/works-with-agents/.co.uk && npx wrangler pages deploy . --project-name workswithagents-couk

# Bastion (Worker)
cd ~/Agent-Projects/bastion-gateway && npx wrangler deploy
```

### Post-deploy verification
```bash
curl -s https://workswithagents.dev/v1/health | jq
curl -s https://workswithagents.dev/v1/skills | jq '.count'
curl -s https://workswithagents.com | head -1
curl -s https://workswithagents.co.uk | head -1
curl -s https://bastiongateway.com/v1/health | jq
```

## Database Setup (first deploy only)

### .dev — D1 databases needed:
- `facts-db` — for FactBase facts
- `heartbeat-db` — for heartbeats, pitfalls, newsletter subs

```bash
npx wrangler d1 create facts-db
npx wrangler d1 create heartbeat-db
```

### Bastion — D1 database needed:
- `bastion-db` — for licenses, usage_log, admin_tokens

```bash
npx wrangler d1 create bastion-db
```

## Environment Variables

None required for local dev. For Cloudflare Workers:
- `.dev`: `SKILLS_DIR` defaults to `~/.hermes/skills/` (local), must be set in Worker to point to skills source
- `Bastion`: `OMLX_HOST` defaults to `http://localhost:8000` for local dev
- `Bastion`: `BASTION_DATA_DIR` defaults to `./data` for local dev

## Monitoring

- Fleet health: `GET https://workswithagents.dev/v1/fleet/health`
- FactBase stats: `GET https://workswithagents.dev/v1/facts/stats`
- Bastion stats: `GET https://bastiongateway.com/v1/admin/stats?admin_token=...`
- Newsletter: `SELECT count(*) FROM newsletter_subs` in heartbeat DB
