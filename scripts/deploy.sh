#!/usr/bin/env bash
# SpyFy — deploy automatizado (compose + cloud tunnel)
# Uso: bash scripts/deploy.sh [up|down|ngrok|tunnel|deploy]
set -euo pipefail
cd "$(dirname "$0")/.."

case "${1:-up}" in
  up)     docker compose up -d ;;
  down)   docker compose down ;;
  ngrok)  docker compose up -d caddy; docker compose run --rm tunnel-ngrok ;;
  tunnel) docker compose up -d caddy; docker compose run --rm tunnel-cloudflare ;;
  deploy) docker compose up -d; docker compose up -d caddy; docker compose run --rm tunnel-cloudflare ;;
  *) echo "uso: $0 [up|down|ngrok|tunnel|deploy]"; exit 1 ;;
esac
