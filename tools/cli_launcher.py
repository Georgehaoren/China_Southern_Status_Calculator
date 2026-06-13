from __future__ import annotations

import argparse
import sys
from pathlib import Path

from launcher_core import LauncherConfig, LauncherError, LocalWebUILauncher, find_project_root

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║  China Southern Status Calculator WebUI Launcher     ║
║  南航明珠等级测算 WebUI 启动器（非官方）             ║
╚══════════════════════════════════════════════════════╝
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the local China Southern Status Calculator WebUI."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=5055, help="Preferred local port. Default: 5055")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically.")
    parser.add_argument("--no-port-fallback", action="store_true", help="Fail instead of using the next free port.")
    parser.add_argument("--reinstall", action="store_true", help="Force reinstall dependencies.")
    parser.add_argument("--reset-venv", action="store_true", help="Delete and recreate .venv before starting.")
    parser.add_argument("--debug", action="store_true", help="Enable verbose launcher mode.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root path. Usually not needed.",
    )
    return parser.parse_args()


def main() -> int:
    print(BANNER)
    args = parse_args()

    try:
        project_root = args.project_root.resolve() if args.project_root else find_project_root(Path(__file__).resolve())
        config = LauncherConfig(
            project_root=project_root,
            host=args.host,
            port=args.port,
            allow_port_fallback=not args.no_port_fallback,
            auto_open_browser=not args.no_browser,
            force_reinstall=args.reinstall,
            reset_venv=args.reset_venv,
            debug=args.debug,
        )
        launcher = LocalWebUILauncher(config)
        return launcher.run_blocking()
    except LauncherError as exc:
        print(f"\n启动失败 / Launch failed:\n{exc}", file=sys.stderr)
        print("\n请查看 logs/launcher.log 和 logs/flask_server.log。", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - launcher should show friendly errors.
        print(f"\n未知错误 / Unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("\n请查看 logs/launcher.log 和 logs/flask_server.log。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
