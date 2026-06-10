#!/usr/bin/env bash
set -euo pipefail

APP_HOST="127.0.0.1"
APP_PORT="5055"
APP_URL="http://${APP_HOST}:${APP_PORT}/"
VENV_DIR=".venv"
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/flask_server.log"

cd "$(dirname "$0")"
mkdir -p "$LOG_DIR"

echo "Using fixed port: ${APP_PORT}"
echo "App URL: ${APP_URL}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Error: Python is not installed or not in PATH."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  "$PYTHON_CMD" -m venv "$VENV_DIR"
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
  # macOS / Linux
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  # Windows Git Bash
  # shellcheck disable=SC1091
  source "$VENV_DIR/Scripts/activate"
else
  echo "Error: Cannot find venv activate script."
  exit 1
fi

echo "Installing required packages..."
python -m pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  pip install flask
fi

if command -v lsof >/dev/null 2>&1; then
  EXISTING_PID=$(lsof -ti tcp:${APP_PORT} || true)
  if [ -n "$EXISTING_PID" ]; then
    echo "Port ${APP_PORT} is in use. Killing existing process: ${EXISTING_PID}"
    kill -9 $EXISTING_PID || true
  fi
fi

export CZ_APP_PORT="$APP_PORT"
: > "$LOG_FILE"

echo "Starting Flask backend..."
python app.py >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!

cleanup() {
  echo "Stopping Flask..."
  kill "$SERVER_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

echo "Waiting for backend..."
for _ in $(seq 1 40); do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo "Flask backend exited early. Log:"
    cat "$LOG_FILE"
    exit 1
  fi
  if python - <<PYWAIT
import urllib.request, sys
try:
    urllib.request.urlopen("${APP_URL}api/health", timeout=1)
except Exception:
    sys.exit(1)
else:
    sys.exit(0)
PYWAIT
  then
    break
  fi
  sleep 0.5
done

echo "Opening browser: ${APP_URL}"
if [ "$(uname)" = "Darwin" ]; then
  /usr/bin/open "${APP_URL}"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${APP_URL}" >/dev/null 2>&1 || true
elif command -v cmd.exe >/dev/null 2>&1; then
  cmd.exe /c start "" "${APP_URL}"
else
  echo "Please open manually: ${APP_URL}"
fi

echo "Backend is running at ${APP_URL}"
echo "Logs: tail -f ${LOG_FILE}"
echo "Press Ctrl+C to stop."
wait "$SERVER_PID"
