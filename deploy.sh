#!/bin/bash
# Deploy Works With Agents + Bastion Gateway
# Hybrid: static sites → Cloudflare Pages, APIs → Hetzner VPS (via rsync+ssh)
# Prerequisites: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, VPS_HOST

set -e

echo "=== Deploying Works With Agents + Bastion Gateway ==="

# ── Pre-Deploy Scrub (BLOCKS if internal content found) ──────────────
echo ""
echo "--- Pre-Deploy Scrub ---"
python3.11 ~/.hermes/scripts/pre-publish-scrub.py --strict
echo ""

# ── Static Sites (Cloudflare Pages) ──────────────────────────────────
echo ""
echo "--- Static Sites: Cloudflare Pages ---"

for site in workswithagents-com workswithagents-couk; do
  dir=$(echo "$site" | sed 's/workswithagents-//')
  echo "  Deploying $dir..."
  cd "$HOME/Agent-Projects/works-with-agents/.$dir"
  npx wrangler pages deploy . --project-name "$site" --branch main
done

# ── APIs (Hetzner VPS) ──────────────────────────────────────────────
if [ -z "$VPS_HOST" ]; then
  echo ""
  echo "⚠️  VPS_HOST not set — skipping API deployments."
  echo "   To deploy .dev, .io, Bastion: set VPS_HOST and run again."
  echo "   Static sites (.com, .co.uk) deployed successfully."
  exit 0
fi

echo ""
echo "--- APIs: rsync → $VPS_HOST ---"

APIS=(
  "workswithagents.dev:.dev/api"
  "workswithagents.io:.io/api"
  "bastiongateway.com:../bastion-gateway/api"
)

for api in "${APIS[@]}"; do
  domain="${api%%:*}"
  src="${api##*:}"
  echo "  Deploying $domain..."

  # Resolve relative path
  if [[ "$src" == ../* ]]; then
    cd "$HOME/Agent-Projects"
    src_path="${src#../}"
  else
    cd "$HOME/Agent-Projects/works-with-agents"
    src_path="$src"
  fi

  rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude 'data/' \
    "$src_path/" "$VPS_HOST:/opt/$domain/"

  # Restart service
  ssh "$VPS_HOST" "sudo systemctl restart $domain"
done

echo ""
echo "=== All deployed ==="
echo "Check: https://workswithagents.com"
echo "Check: https://workswithagents.co.uk"
echo "Check: https://workswithagents.dev/v1/health"
echo "Check: https://workswithagents.io/v1/health"
echo "Check: https://bastiongateway.com/v1/health"

echo ""
echo "DNS must be configured: all domains → VPS IP (orange-cloud ON)."
echo "Static sites (.com, .co.uk) served via Cloudflare Pages CNAME."
echo "APIs (.dev, .io, bastiongateway) served via Cloudflare → VPS proxy."
