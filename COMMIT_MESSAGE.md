feat: add CLI and GUI launchers for local WebUI

Add a shared launcher layer for the local Flask WebUI so beginner users can start the project without manually creating a virtual environment or running pip commands.

Changes:
- Add shared launcher core in `tools/launcher_core.py`.
- Add command-line launcher in `tools/cli_launcher.py`.
- Add graphical launcher in `tools/gui_launcher.py`.
- Add Windows/macOS/Linux entry scripts:
  - `start.bat`
  - `start_cli.bat`
  - `start.command`
  - `start.sh`
  - `start_gui.sh`
- Add optional GUI dependency file `requirements-gui.txt`.
- Add beginner-friendly startup guide `README_BEGINNER.md`.
- Add launcher design and packaging strategy docs.

The launcher now handles:
- Project root detection.
- `.venv` creation and reuse.
- Dependency installation from `requirements.txt`.
- Port availability checks and automatic fallback.
- Flask startup through `CZ_APP_PORT`.
- Health check through `/api/health`, with root page fallback.
- Browser auto-open.
- Runtime logs under `logs/`.
- Graceful backend stop from CLI or GUI.

This keeps the calculator itself unchanged and adds a beginner-friendly local WebUI management layer.
