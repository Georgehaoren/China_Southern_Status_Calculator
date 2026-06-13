#!/usr/bin/env bash
# China Southern Status Calculator - Local WebUI starter
# 南航明珠等级测算器 - 本地 WebUI 启动脚本
#
# This script is intentionally self-contained:
# - It can run even if tools/cli_launcher.py is not present.
# - It creates/reuses .venv, installs dependencies, starts Flask,
#   checks readiness, opens the browser, and writes logs.

set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Locate project root
# -----------------------------------------------------------------------------
SCRIPT_SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SCRIPT_SOURCE" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_SOURCE")" >/dev/null 2>&1 && pwd)"
  SCRIPT_SOURCE="$(readlink "$SCRIPT_SOURCE")"
  [[ "$SCRIPT_SOURCE" != /* ]] && SCRIPT_SOURCE="$SCRIPT_DIR/$SCRIPT_SOURCE"
done
PROJECT_ROOT="$(cd -P "$(dirname "$SCRIPT_SOURCE")" >/dev/null 2>&1 && pwd)"
cd "$PROJECT_ROOT"

# -----------------------------------------------------------------------------
# Defaults. These may be overridden by environment variables or CLI arguments.
# -----------------------------------------------------------------------------
APP_HOST="${CZ_APP_HOST:-127.0.0.1}"
APP_PORT="${CZ_APP_PORT:-5055}"
VENV_DIR="${CZ_VENV_DIR:-.venv}"
LOG_DIR="${CZ_LOG_DIR:-logs}"
SERVER_LOG_FILE="$LOG_DIR/flask_server.log"
LAUNCHER_LOG_FILE="$LOG_DIR/launcher.log"
HEALTH_PATH="${CZ_HEALTH_PATH:-/api/health}"
MAX_PORT_TRIES="${CZ_MAX_PORT_TRIES:-20}"

AUTO_OPEN_BROWSER=1
ALLOW_PORT_FALLBACK=1
FORCE_REINSTALL=0
RESET_VENV=0
DEBUG_MODE=0
KILL_PORT=0
USE_PYTHON_LAUNCHER=0
SERVER_PID=""
APP_URL=""

# -----------------------------------------------------------------------------
# Small UI helpers
# -----------------------------------------------------------------------------
print_banner() {
  cat <<'BANNER'
╔══════════════════════════════════════════════════════╗
║  China Southern Status Calculator WebUI Launcher     ║
║  南航明珠等级测算 WebUI 启动器（非官方）               ║
╚══════════════════════════════════════════════════════╝
BANNER
}

log() {
  mkdir -p "$LOG_DIR"
  local message="$*"
  local timestamp
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "$message"
  printf '[%s] %s\n' "$timestamp" "$message" >> "$LAUNCHER_LOG_FILE" 2>/dev/null || true
}

log_step() {
  log ""
  log "==> $*"
}

fail() {
  log ""
  log "启动失败 / Launch failed: $*"
  log "请查看日志 / Please check logs:"
  log "  $LAUNCHER_LOG_FILE"
  log "  $SERVER_LOG_FILE"
  exit 1
}

show_help() {
  cat <<'HELP'
Usage:
  ./start.sh [options]

Options:
  --host HOST             Host to bind. Default: 127.0.0.1
  --port PORT             Preferred port. Default: 5055
  --no-browser            Do not open browser automatically.
  --no-port-fallback      Fail if the preferred port is occupied.
  --kill-port             Kill the existing process on the preferred port.
                          Use with care. Disabled by default.
  --reinstall             Force reinstall dependencies from requirements.txt.
  --reset-venv            Delete and recreate .venv before starting.
  --debug                 Print more diagnostic information.
  --python-launcher       Delegate to tools/cli_launcher.py if available.
  -h, --help              Show this help message.

Examples:
  ./start.sh
  ./start.sh --port 5056
  ./start.sh --no-browser
  ./start.sh --reset-venv
HELP
}

# -----------------------------------------------------------------------------
# Parse arguments
# -----------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      [[ $# -ge 2 ]] || fail "--host requires a value."
      APP_HOST="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || fail "--port requires a value."
      APP_PORT="$2"
      shift 2
      ;;
    --no-browser)
      AUTO_OPEN_BROWSER=0
      shift
      ;;
    --no-port-fallback)
      ALLOW_PORT_FALLBACK=0
      shift
      ;;
    --kill-port)
      KILL_PORT=1
      ALLOW_PORT_FALLBACK=0
      shift
      ;;
    --reinstall)
      FORCE_REINSTALL=1
      shift
      ;;
    --reset-venv)
      RESET_VENV=1
      shift
      ;;
    --debug)
      DEBUG_MODE=1
      shift
      ;;
    --python-launcher)
      USE_PYTHON_LAUNCHER=1
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      fail "Unknown option: $1"
      ;;
  esac
done

if ! [[ "$APP_PORT" =~ ^[0-9]+$ ]]; then
  fail "Port must be a number: $APP_PORT"
fi

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
cleanup() {
  local exit_code=$?
  if [[ -n "${SERVER_PID:-}" ]]; then
    if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
      log ""
      log "Stopping Flask backend..."
      kill "$SERVER_PID" >/dev/null 2>&1 || true
      wait "$SERVER_PID" >/dev/null 2>&1 || true
    fi
  fi
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

# -----------------------------------------------------------------------------
# Python detection
# -----------------------------------------------------------------------------
find_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
  elif command -v python >/dev/null 2>&1; then
    echo "python"
  else
    return 1
  fi
}

validate_python() {
  local python_cmd="$1"
  "$python_cmd" - <<'PY'
import sys
if sys.version_info < (3, 9):
    print(f"Python 3.9+ is recommended. Current: {sys.version.split()[0]}")
    raise SystemExit(1)
print(sys.version.split()[0])
PY
}

PYTHON_CMD="$(find_python || true)"
[[ -n "$PYTHON_CMD" ]] || fail "Python is not installed or not in PATH. Please install Python 3.9+ first."
PYTHON_VERSION="$(validate_python "$PYTHON_CMD" 2>/dev/null)" || fail "Python 3.9+ is required or strongly recommended. Current Python command: $PYTHON_CMD"

print_banner
log "Project root: $PROJECT_ROOT"
log "Python: $PYTHON_CMD ($PYTHON_VERSION)"
log "Preferred URL: http://$APP_HOST:$APP_PORT/"

# -----------------------------------------------------------------------------
# Optional: delegate to Python CLI launcher from the new launcher architecture.
# Disabled by default so this shell script remains a full standalone launcher.
# -----------------------------------------------------------------------------
if [[ "$USE_PYTHON_LAUNCHER" -eq 1 && -f "tools/cli_launcher.py" ]]; then
  log_step "Delegating to tools/cli_launcher.py"
  CLI_ARGS=("tools/cli_launcher.py" "--host" "$APP_HOST" "--port" "$APP_PORT")
  [[ "$AUTO_OPEN_BROWSER" -eq 0 ]] && CLI_ARGS+=("--no-browser")
  [[ "$ALLOW_PORT_FALLBACK" -eq 0 ]] && CLI_ARGS+=("--no-port-fallback")
  [[ "$FORCE_REINSTALL" -eq 1 ]] && CLI_ARGS+=("--reinstall")
  [[ "$RESET_VENV" -eq 1 ]] && CLI_ARGS+=("--reset-venv")
  [[ "$DEBUG_MODE" -eq 1 ]] && CLI_ARGS+=("--debug")
  exec "$PYTHON_CMD" "${CLI_ARGS[@]}"
fi

# -----------------------------------------------------------------------------
# Project validation
# -----------------------------------------------------------------------------
[[ -f "app.py" ]] || fail "Cannot find app.py. Please run start.sh from the project root."
if [[ ! -f "requirements.txt" ]]; then
  log "Warning: requirements.txt not found. Flask fallback will be installed."
fi
mkdir -p "$LOG_DIR"

# -----------------------------------------------------------------------------
# Virtual environment
# -----------------------------------------------------------------------------
venv_python_path() {
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    echo "$VENV_DIR/bin/python"
  elif [[ -x "$VENV_DIR/Scripts/python.exe" ]]; then
    echo "$VENV_DIR/Scripts/python.exe"
  elif [[ -x "$VENV_DIR/Scripts/python" ]]; then
    echo "$VENV_DIR/Scripts/python"
  else
    return 1
  fi
}

if [[ "$RESET_VENV" -eq 1 && -d "$VENV_DIR" ]]; then
  log_step "Removing existing virtual environment"
  rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  log_step "Creating virtual environment: $VENV_DIR"
  "$PYTHON_CMD" -m venv "$VENV_DIR" || fail "Failed to create virtual environment."
else
  log_step "Using existing virtual environment: $VENV_DIR"
fi

APP_PYTHON="$(venv_python_path || true)"
[[ -n "$APP_PYTHON" ]] || fail "Cannot find Python executable inside $VENV_DIR. Try: ./start.sh --reset-venv"

# Activate venv when possible. The script also uses APP_PYTHON directly, so activation
# is mostly for nicer PATH behavior and compatibility with older workflows.
if [[ -f "$VENV_DIR/bin/activate" ]]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/Scripts/activate"
fi

# -----------------------------------------------------------------------------
# Dependency installation with a small requirements hash stamp
# -----------------------------------------------------------------------------
requirements_hash() {
  if [[ -f "requirements.txt" ]]; then
    "$APP_PYTHON" - <<'PY'
from pathlib import Path
import hashlib
path = Path("requirements.txt")
print(hashlib.sha256(path.read_bytes()).hexdigest())
PY
  else
    echo "no-requirements"
  fi
}

DEPS_STAMP="$VENV_DIR/.czcalc_requirements.sha256"
CURRENT_REQ_HASH="$(requirements_hash)"
INSTALLED_REQ_HASH=""
[[ -f "$DEPS_STAMP" ]] && INSTALLED_REQ_HASH="$(cat "$DEPS_STAMP" 2>/dev/null || true)"

if [[ "$FORCE_REINSTALL" -eq 1 || "$CURRENT_REQ_HASH" != "$INSTALLED_REQ_HASH" ]]; then
  log_step "Installing dependencies"
  "$APP_PYTHON" -m pip install --upgrade pip || fail "Failed to upgrade pip."
  if [[ -f "requirements.txt" ]]; then
    "$APP_PYTHON" -m pip install -r requirements.txt || fail "Failed to install requirements.txt."
  else
    "$APP_PYTHON" -m pip install "Flask>=3.0.0" || fail "Failed to install Flask fallback."
  fi
  printf '%s\n' "$CURRENT_REQ_HASH" > "$DEPS_STAMP" || true
else
  log_step "Dependencies are already up to date"
fi

# -----------------------------------------------------------------------------
# Port handling
# -----------------------------------------------------------------------------
is_port_open() {
  local host="$1"
  local port="$2"
  "$APP_PYTHON" - "$host" "$port" <<'PY'
import socket
import sys
host = sys.argv[1]
port = int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.4)
    raise SystemExit(0 if sock.connect_ex((host, port)) == 0 else 1)
PY
}

kill_port_process() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti tcp:"$port" || true)"
    if [[ -n "$pids" ]]; then
      log "Port $port is in use. Killing existing process(es): $pids"
      # shellcheck disable=SC2086
      kill -9 $pids >/dev/null 2>&1 || true
    fi
  else
    fail "Port $port is in use and lsof is not available. Close the process manually or run with another --port."
  fi
}

choose_port() {
  local host="$1"
  local requested_port="$2"
  local port

  if ! is_port_open "$host" "$requested_port"; then
    echo "$requested_port"
    return 0
  fi

  if [[ "$KILL_PORT" -eq 1 ]]; then
    kill_port_process "$requested_port"
    echo "$requested_port"
    return 0
  fi

  if [[ "$ALLOW_PORT_FALLBACK" -eq 0 ]]; then
    fail "Port $requested_port is already in use. Use --port, close the other app, or add --kill-port."
  fi

  for ((port = requested_port + 1; port <= requested_port + MAX_PORT_TRIES; port++)); do
    if ! is_port_open "$host" "$port"; then
      log "Port $requested_port is busy; using port $port instead."
      echo "$port"
      return 0
    fi
  done

  fail "No free port found from $requested_port to $((requested_port + MAX_PORT_TRIES))."
}

ACTIVE_PORT="$(choose_port "$APP_HOST" "$APP_PORT")"
APP_URL="http://$APP_HOST:$ACTIVE_PORT/"

# -----------------------------------------------------------------------------
# Start Flask backend
# -----------------------------------------------------------------------------
log_step "Starting Flask backend"
: > "$SERVER_LOG_FILE"
{
  echo "================================================================================"
  echo "Starting Flask backend at $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Project root: $PROJECT_ROOT"
  echo "URL: $APP_URL"
  echo "================================================================================"
} >> "$SERVER_LOG_FILE"

export CZ_APP_HOST="$APP_HOST"
export CZ_APP_PORT="$ACTIVE_PORT"
export PYTHONUNBUFFERED=1

"$APP_PYTHON" app.py >> "$SERVER_LOG_FILE" 2>&1 &
SERVER_PID=$!
log "Flask PID: $SERVER_PID"
log "Log file: $SERVER_LOG_FILE"

# -----------------------------------------------------------------------------
# Readiness check: try /api/health first, then / as fallback.
# -----------------------------------------------------------------------------
check_url() {
  local url="$1"
  "$APP_PYTHON" - "$url" <<'PY'
import sys
import urllib.error
import urllib.request
url = sys.argv[1]
try:
    with urllib.request.urlopen(url, timeout=1.5) as response:
        # For a local WebUI, any non-5xx response means the server is alive.
        raise SystemExit(0 if response.status < 500 else 1)
except Exception:
    raise SystemExit(1)
PY
}

log_step "Waiting for WebUI to become ready"
READY=0
HEALTH_URL="http://$APP_HOST:$ACTIVE_PORT$HEALTH_PATH"
ROOT_URL="$APP_URL"

for _ in $(seq 1 60); do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    log "Flask backend exited early. Recent server log:"
    if command -v tail >/dev/null 2>&1; then
      tail -n 80 "$SERVER_LOG_FILE" || true
    else
      cat "$SERVER_LOG_FILE" || true
    fi
    fail "Flask backend exited before becoming ready."
  fi

  if check_url "$HEALTH_URL" || check_url "$ROOT_URL"; then
    READY=1
    break
  fi

  sleep 0.5
done

[[ "$READY" -eq 1 ]] || fail "WebUI did not become ready in time."

# -----------------------------------------------------------------------------
# Open browser
# -----------------------------------------------------------------------------
open_browser() {
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "$url" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || true
  elif command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start "" "$url" >/dev/null 2>&1 || true
  else
    return 1
  fi
}

log ""
log "WebUI is running at: $APP_URL"
log "Logs: tail -f $SERVER_LOG_FILE"
log "Press Ctrl+C to stop."

if [[ "$AUTO_OPEN_BROWSER" -eq 1 ]]; then
  log "Opening browser..."
  if ! open_browser "$APP_URL"; then
    log "Cannot open browser automatically. Please open manually: $APP_URL"
  fi
else
  log "Browser auto-open disabled. Please open manually: $APP_URL"
fi

# Keep the script alive so Ctrl+C can stop Flask.
wait "$SERVER_PID"
