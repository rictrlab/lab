#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "== RictrLab Serve =="
 
# Check backend
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "✓ Backend already running on :8000 (PID $(ps aux | grep '[u]vicorn' | awk '{print $2}' | head -1))"
else
  echo "Starting backend on :8000..."
  cd "$ROOT/backend"
  nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/rictrlab-backend.log 2>&1 &
  sleep 3
  curl -s http://localhost:8000/api/health | python3 -m json.tool
fi

# Check frontend
if curl -s http://localhost:3000 2>&1 | grep -q RictrLab; then
  echo "✓ Frontend already running on :3000 (PID $(ps aux | grep '[n]ext-server' | awk '{print $2}' | head -1))"
else
  if ss -tlnp 2>/dev/null | grep -q 3000; then
    echo "Port 3000 in use but not responding, restarting..."
    pkill -f "next start" || true
    sleep 2
  fi
  echo "Starting frontend on :3000..."
  cd "$ROOT/frontend"
  nohup npm run start > /tmp/rictrlab-frontend.log 2>&1 &
  sleep 5
  curl -s -I http://localhost:3000 | head -n 5
fi

echo ""
echo "== RictrLab Running =="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Health:   http://localhost:8000/api/health"
echo ""
echo "Logs:"
echo "  backend:  tail -f /tmp/rictrlab-backend.log"
echo "  frontend: tail -f /tmp/rictrlab-frontend.log"
