#!/bin/bash
# Deploy Works With Agents
# Hybrid: static redirects → Cloudflare Pages, API → Hetzner VPS (via rsync+ssh)
# Prerequisites: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, VPS_HOST

set -e

echo "=== Deploying Works With Agents ==="

# ── Pre-Deploy Scrub (BLOCKS if internal content found) ──────────────
echo ""
echo "--- Pre-Deploy Scrub ---"
python3.11 ~/.hermes/scripts/pre-publish-scrub.py --strict
echo ""

# ── Static Redirects (Cloudflare Pages) ────────────────────────────
echo ""
echo "--- Static Redirects: Cloudflare Pages ---"

for site in workswithagents-com workswithagents-couk; do
  dir=$(echo "$site" | sed 's/workswithagents-//')
  echo "  Deploying $dir..."
  cd "$HOME/Agent-Projects/works-with-agents/.$dir"
  npx wrangler pages deploy . --project-name "$site" --branch main
done

# ── API (Hetzner VPS) ──────────────────────────────────────────────
if [ -z "$VPS_HOST" ]; then
  echo ""
  echo "⚠️  VPS_HOST not set — skipping API deployment."
  exit 0
fi

echo ""
echo "--- API: rsync → $VPS_HOST ---"

DOMAIN="workswithagents.dev"
SRC=".dev/api"
cd "$HOME/Agent-Projects/works-with-agents"
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude 'data/' \
  "$SRC/" "$VPS_HOST:/opt/$DOMAIN/"

# Also sync specs + llms files
rsync -avz .dev/specs/ .dev/llms.txt .dev/llms-full.txt "$VPS_HOST:/opt/works-with-agents/.dev/"

ssh "$VPS_HOST" "sudo systemctl restart wwa-dev"

echo ""
echo "=== Deployed ==="
echo "https://workswithagents.dev"
