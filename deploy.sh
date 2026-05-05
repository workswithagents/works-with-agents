#!/bin/bash
# Deploy all Works With Agents + Bastion Gateway sites to Cloudflare
# Prerequisites: npx wrangler login, Cloudflare account with DNS zones configured

set -e

echo "=== Deploying Works With Agents ==="

# .dev — API Worker
echo ""
echo "--- workswithagents.dev (API Worker) ---"
cd "$HOME/Agent-Projects/works-with-agents/.dev"
npx wrangler deploy --env production

# .com — Pages
echo ""
echo "--- workswithagents.com (Pages) ---"
cd "$HOME/Agent-Projects/works-with-agents/.com"
npx wrangler pages deploy . --project-name workswithagents-com --branch main

# .co.uk — Pages
echo ""
echo "--- workswithagents.co.uk (Pages) ---"
cd "$HOME/Agent-Projects/works-with-agents/.co.uk"
npx wrangler pages deploy . --project-name workswithagents-couk --branch main

# Bastion Gateway — API Worker
echo ""
echo "--- bastiongateway.com (API Worker) ---"
cd "$HOME/Agent-Projects/bastion-gateway"
npx wrangler deploy --env production

echo ""
echo "=== All deployed ==="
echo "Check: https://workswithagents.dev/v1/health"
echo "Check: https://workswithagents.com"
echo "Check: https://workswithagents.co.uk"
echo "Check: https://bastiongateway.com/v1/health"

# Note: DNS must already be configured in Cloudflare for these zones.
# Workers/Functions routes assume the domains are in your Cloudflare account.
