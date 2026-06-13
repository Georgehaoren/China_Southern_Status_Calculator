#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export PYTHONUTF8=1

if command -v python3 >/dev/null 2>&1; then
  python3 tools/gui_launcher.py
elif command -v python >/dev/null 2>&1; then
  python tools/gui_launcher.py
else
  echo "Error: Python was not found. Please install Python 3.10+."
  exit 1
fi
