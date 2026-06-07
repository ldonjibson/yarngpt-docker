#!/usr/bin/env bash
set -euo pipefail

LOGFILE="cloudflared.log"

# Kill any existing cloudflared tunnel on port 8000
pkill -f "cloudflared tunnel.*8000" 2>/dev/null || true
rm -f "$LOGFILE"

nohup cloudflared tunnel --url http://localhost:8000 > "$LOGFILE" 2>&1 &
PID=$!
echo "cloudflared started (PID $PID) — waiting for URL..."

# Poll until the trycloudflare URL appears
while ! grep -q 'https://.*\.trycloudflare\.com' "$LOGFILE" 2>/dev/null; do
  sleep 1
done

URL=$(grep -o 'https://[a-z-]*\.trycloudflare\.com' "$LOGFILE" | head -1)
echo "Tunnel URL: $URL"
