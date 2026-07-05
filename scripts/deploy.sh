#!/usr/bin/env bash
# Build the static site and deploy it to Cloudflare (your-site.example.com).
# Usage: bash scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> building dist/"
uv run python -m mama_site.cli

echo "==> deploying to Cloudflare"
npx wrangler@latest deploy

echo "==> live check (via --resolve, bypasses local DNS cache)"
IP="$(dig +short your-site.example.com | head -1)"
curl -s --resolve "your-site.example.com:443:${IP}" -o /dev/null \
  -w "your-site.example.com -> http %{http_code}\n" https://your-site.example.com/
