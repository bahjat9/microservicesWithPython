#!/usr/bin/env bash

# change these variables to fit your working directory !! 🚨

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOLUTION="$SCRIPT_DIR/services"
NOTIFICATION="$SCRIPT_DIR/services/notification-service"

PIDS=()

cleanup() {
  echo ""
  echo "Stopping all services..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  exit 0
}

trap cleanup SIGINT SIGTERM

run_uvicorn() {
  local name="$1"
  local port="$2"
  local dir="$SOLUTION/$name"

  if [ ! -f "$dir/app/main.py" ]; then
    echo "[$name] skipping — no app/main.py"
    return
  fi

  local pip
  if [ -f "$dir/.venv/Scripts/pip" ]; then
    pip="$dir/.venv/Scripts/pip"
  elif [ -f "$dir/.venv/bin/pip" ]; then
    pip="$dir/.venv/bin/pip"
  fi

  if [ -n "$pip" ] && [ -f "$dir/requirements.txt" ]; then
    echo "[$name] installing requirements..."
    (cd "$dir" && "$pip" install -r requirements.txt -q)
  fi

  local uvicorn
  if [ -f "$dir/.venv/Scripts/uvicorn" ]; then
    uvicorn="$dir/.venv/Scripts/uvicorn"
  elif [ -f "$dir/.venv/bin/uvicorn" ]; then
    uvicorn="$dir/.venv/bin/uvicorn"
  else
    echo "[$name] skipping — no uvicorn in .venv"
    return
  fi

  echo "[$name] -> http://localhost:$port"
  (cd "$dir" && "$uvicorn" app.main:app --port "$port" --reload) &
  PIDS+=($!)
}

run_flask() {
  local name="$1"
  local port="$2"
  local dir="$SOLUTION/$name"

  if [ ! -f "$dir/app/main.py" ]; then
    echo "[$name] skipping — no app/main.py"
    return
  fi

  local pip
  if [ -f "$dir/.venv/Scripts/pip" ]; then
    pip="$dir/.venv/Scripts/pip"
  elif [ -f "$dir/.venv/bin/pip" ]; then
    pip="$dir/.venv/bin/pip"
  fi

  if [ -n "$pip" ] && [ -f "$dir/requirements.txt" ]; then
    echo "[$name] installing requirements..."
    (cd "$dir" && "$pip" install -r requirements.txt -q)
  fi

  local flask
  if [ -f "$dir/.venv/Scripts/flask" ]; then
    flask="$dir/.venv/Scripts/flask"
  elif [ -f "$dir/.venv/bin/flask" ]; then
    flask="$dir/.venv/bin/flask"
  else
    echo "[$name] skipping — no flask in .venv"
    return
  fi

  echo "[$name] -> http://localhost:$port"
  (cd "$dir" && "$flask" --app app.main run --port "$port") &
  PIDS+=($!)
}

# FastAPI / uvicorn services
run_uvicorn "gateway"           8000
run_uvicorn "user-service"      8001
run_uvicorn "game-service"      8002
run_uvicorn "activity-service"  8003
run_uvicorn "auth-service"      8005

# Flask / WSGI service
run_flask   "logging-service"   8006

# Node.js service (lives in services/, not solution/)
if [ -f "$NOTIFICATION/package.json" ]; then
  echo "[notification-service] -> http://localhost:8004"
  (cd "$NOTIFICATION" && nvm use 20.20.2 && npm install && npm run dev) &
  PIDS+=($!)
else
  echo "[notification-service] skipping — no package.json"
fi

echo ""
echo "Press Ctrl+C to stop all services."
wait "${PIDS[@]}"