from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

LogCallback = Callable[[str], None]


class LauncherError(RuntimeError):
    """Raised when the local WebUI launcher cannot continue."""


@dataclass
class LauncherConfig:
    """Configuration shared by CLI and GUI launchers."""

    project_root: Path
    host: str = "127.0.0.1"
    port: int = 5055
    allow_port_fallback: bool = True
    auto_open_browser: bool = True
    force_reinstall: bool = False
    reset_venv: bool = False
    debug: bool = False
    app_file: str = "app.py"
    requirements_file: str = "requirements.txt"
    venv_dir: str = ".venv"
    log_dir: str = "logs"
    launcher_log_name: str = "launcher.log"
    server_log_name: str = "flask_server.log"
    health_path: str = "/api/health"

    @property
    def venv_path(self) -> Path:
        return self.project_root / self.venv_dir

    @property
    def log_path(self) -> Path:
        return self.project_root / self.log_dir

    @property
    def launcher_log_file(self) -> Path:
        return self.log_path / self.launcher_log_name

    @property
    def server_log_file(self) -> Path:
        return self.log_path / self.server_log_name

    @property
    def requirements_path(self) -> Path:
        return self.project_root / self.requirements_file

    @property
    def app_path(self) -> Path:
        return self.project_root / self.app_file


def find_project_root(start: Optional[Path] = None) -> Path:
    """Find the repository root by walking upward until app.py is found."""

    current = (start or Path(__file__).resolve()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "app.py").exists() and (candidate / "requirements.txt").exists():
            return candidate

    raise LauncherError(
        "Cannot find project root. Please run this launcher inside the "
        "China_Southern_Status_Calculator repository."
    )


def default_python_executable() -> str:
    """Return the current Python executable used to create the venv."""

    return sys.executable or "python"


def venv_python(venv_path: Path) -> Path:
    """Return the Python executable inside a virtual environment."""

    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def is_port_open(host: str, port: int) -> bool:
    """Check whether something is already listening on host:port."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def choose_port(host: str, requested_port: int, allow_fallback: bool, max_tries: int = 20) -> int:
    """Choose requested_port if free, otherwise find the next free port."""

    if not is_port_open(host, requested_port):
        return requested_port

    if not allow_fallback:
        raise LauncherError(
            f"Port {requested_port} is already in use. Close the other program or use --port."
        )

    for port in range(requested_port + 1, requested_port + max_tries + 1):
        if not is_port_open(host, port):
            return port

    raise LauncherError(
        f"Ports {requested_port}-{requested_port + max_tries} are all in use. "
        "Please close other local services and try again."
    )


def safe_kill_process(process: Optional[subprocess.Popen]) -> None:
    """Stop a server process without raising errors."""

    if process is None or process.poll() is not None:
        return

    try:
        if os.name == "nt":
            process.terminate()
        else:
            process.send_signal(signal.SIGTERM)
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


class LocalWebUILauncher:
    """Shared local WebUI launcher used by both CLI and GUI frontends."""

    def __init__(self, config: LauncherConfig, log_callback: Optional[LogCallback] = None) -> None:
        self.config = config
        self.log_callback = log_callback
        self.process: Optional[subprocess.Popen] = None
        self.active_port: int = config.port
        self.url: str = self._make_url(config.port)

        self.config.log_path.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        try:
            with self.config.launcher_log_file.open("a", encoding="utf-8") as file:
                file.write(line + "\n")
        except OSError:
            pass

        if self.log_callback:
            self.log_callback(message)
        else:
            print(message, flush=True)

    def _make_url(self, port: int, path: str = "/") -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"http://{self.config.host}:{port}{path}"

    def _run_command(self, command: Iterable[str], description: str) -> None:
        command_list = [str(part) for part in command]
        self.log(description)
        self.log("$ " + " ".join(command_list))

        process = subprocess.Popen(
            command_list,
            cwd=str(self.config.project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        assert process.stdout is not None
        for line in process.stdout:
            self.log(line.rstrip())

        return_code = process.wait()
        if return_code != 0:
            raise LauncherError(f"Command failed with exit code {return_code}: {' '.join(command_list)}")

    def validate_project(self) -> None:
        if not self.config.app_path.exists():
            raise LauncherError(f"Cannot find {self.config.app_file} in project root.")
        if not self.config.requirements_path.exists():
            self.log("requirements.txt not found; Flask will be installed as fallback.")

    def prepare_environment(self) -> Path:
        """Create or reuse .venv and install dependencies."""

        self.validate_project()
        python_exe = default_python_executable()
        venv_path = self.config.venv_path

        if self.config.reset_venv and venv_path.exists():
            self.log("Removing existing virtual environment because reset_venv=True...")
            shutil.rmtree(venv_path)

        if not venv_path.exists():
            self._run_command(
                [python_exe, "-m", "venv", str(venv_path)],
                "Creating local virtual environment...",
            )
        else:
            self.log("Using existing local virtual environment.")

        app_python = venv_python(venv_path)
        if not app_python.exists():
            raise LauncherError(
                "Virtual environment exists, but Python executable was not found inside it. "
                "Try running with --reset-venv."
            )

        self._run_command(
            [str(app_python), "-m", "pip", "install", "--upgrade", "pip"],
            "Upgrading pip inside .venv...",
        )

        if self.config.requirements_path.exists():
            install_cmd = [str(app_python), "-m", "pip", "install"]
            if self.config.force_reinstall:
                install_cmd.append("--force-reinstall")
            install_cmd.extend(["-r", str(self.config.requirements_path)])
            self._run_command(install_cmd, "Installing project dependencies...")
        else:
            self._run_command([str(app_python), "-m", "pip", "install", "Flask>=3.0.0"], "Installing Flask fallback...")

        return app_python

    def start_server(self, app_python: Optional[Path] = None) -> str:
        """Start Flask server and return the WebUI URL."""

        if self.process and self.process.poll() is None:
            self.log(f"Server is already running at {self.url}")
            return self.url

        app_python = app_python or venv_python(self.config.venv_path)
        self.active_port = choose_port(
            self.config.host,
            self.config.port,
            self.config.allow_port_fallback,
        )
        self.url = self._make_url(self.active_port)

        if self.active_port != self.config.port:
            self.log(f"Port {self.config.port} is busy; using port {self.active_port} instead.")

        env = os.environ.copy()
        env["CZ_APP_PORT"] = str(self.active_port)
        env["PYTHONUNBUFFERED"] = "1"

        self.config.server_log_file.parent.mkdir(parents=True, exist_ok=True)
        server_log = self.config.server_log_file.open("a", encoding="utf-8")
        server_log.write("\n" + "=" * 80 + "\n")
        server_log.write(f"Starting server at {time.strftime('%Y-%m-%d %H:%M:%S')} on {self.url}\n")
        server_log.flush()

        self.log("Starting Flask WebUI backend...")
        self.process = subprocess.Popen(
            [str(app_python), str(self.config.app_path)],
            cwd=str(self.config.project_root),
            stdout=server_log,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
        )
        return self.url

    def wait_until_ready(self, timeout_seconds: float = 30.0) -> None:
        """Wait until /api/health or / responds successfully."""

        deadline = time.time() + timeout_seconds
        health_url = self._make_url(self.active_port, self.config.health_path)
        root_url = self._make_url(self.active_port, "/")
        last_error = ""

        self.log("Waiting for WebUI to become ready...")
        while time.time() < deadline:
            if self.process and self.process.poll() is not None:
                raise LauncherError(
                    "Flask backend exited early. Please check logs/flask_server.log."
                )

            for url in (health_url, root_url):
                try:
                    with urllib.request.urlopen(url, timeout=1.5) as response:
                        if 200 <= response.status < 500:
                            self.log(f"WebUI is ready: {self.url}")
                            return
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    last_error = str(exc)

            time.sleep(0.5)

        raise LauncherError(f"WebUI did not become ready in time. Last error: {last_error}")

    def open_browser(self) -> None:
        self.log(f"Opening browser: {self.url}")
        webbrowser.open(self.url)

    def stop_server(self) -> None:
        self.log("Stopping Flask WebUI backend...")
        safe_kill_process(self.process)
        self.process = None
        self.log("Server stopped.")

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def run_blocking(self) -> int:
        """Prepare environment, start WebUI, open browser, and wait until interrupted."""

        app_python = self.prepare_environment()
        self.start_server(app_python)
        self.wait_until_ready()
        if self.config.auto_open_browser:
            self.open_browser()

        self.log("Press Ctrl+C to stop the local WebUI.")
        try:
            assert self.process is not None
            return self.process.wait()
        except KeyboardInterrupt:
            self.log("Ctrl+C received.")
            return 0
        finally:
            self.stop_server()
