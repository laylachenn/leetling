#!/bin/bash
# Serve the web app locally: http://localhost:8000 on this Mac, or http://<this Mac's IP>:8000
# from an iPhone on the same Wi-Fi (handy for a quick look; for the real Home Screen app use the
# GitHub Pages URL, since offline mode needs https).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_web.py
PORT="${PORT:-8000}"
IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
echo "🐰 Leetling web: http://localhost:$PORT${IP:+  ·  iPhone on the same Wi-Fi: http://$IP:$PORT}"
exec python3 -m http.server "$PORT" --directory web
