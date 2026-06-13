from __future__ import annotations

import queue
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import END, BOTH, LEFT, RIGHT, X, Y, filedialog, messagebox

try:
    import customtkinter as ctk

    HAS_CUSTOMTKINTER = True
except Exception:  # pragma: no cover - fallback for machines without CustomTkinter.
    import tkinter as ctk  # type: ignore[no-redef]

    HAS_CUSTOMTKINTER = False

from launcher_core import LauncherConfig, LauncherError, LocalWebUILauncher, find_project_root

APP_TITLE = "南航明珠等级测算 WebUI 启动器"
APP_SUBTITLE = "China Southern Status Calculator Launcher · Unofficial Local WebUI"
DISCLAIMER = "非官方本地测算工具。计算结果仅供规划参考，请以南航明珠及相关航司官方规则和最终入账为准。"


class LauncherGUI:
    def __init__(self) -> None:
        self.project_root = find_project_root(Path(__file__).resolve())
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.launcher: LocalWebUILauncher | None = None
        self.current_url = "http://127.0.0.1:5055/"

        if HAS_CUSTOMTKINTER:
            ctk.set_appearance_mode("System")
            ctk.set_default_color_theme("blue")
            self.root = ctk.CTk()
            self._build_customtkinter_ui()
        else:
            self.root = ctk.Tk()
            self._build_tkinter_ui()

        self.root.title(APP_TITLE)
        self.root.geometry("860x620")
        self.root.minsize(760, 520)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(120, self._drain_log_queue)
        self._set_status("未启动", "gray")

    # ---------- UI construction ----------
    def _build_customtkinter_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self.root, corner_radius=16)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=APP_TITLE, font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=18, pady=(16, 2), sticky="w"
        )
        ctk.CTkLabel(header, text=APP_SUBTITLE, font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=18, pady=(0, 14), sticky="w"
        )

        status_frame = ctk.CTkFrame(self.root, corner_radius=16)
        status_frame.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)

        self.status_dot = ctk.CTkLabel(status_frame, text="●", font=ctk.CTkFont(size=20))
        self.status_dot.grid(row=0, column=0, padx=(18, 6), pady=14, sticky="w")
        self.status_label = ctk.CTkLabel(status_frame, text="未启动", font=ctk.CTkFont(size=15, weight="bold"))
        self.status_label.grid(row=0, column=1, padx=4, pady=14, sticky="w")
        self.url_label = ctk.CTkLabel(status_frame, text=self.current_url)
        self.url_label.grid(row=0, column=2, padx=18, pady=14, sticky="e")

        actions = ctk.CTkFrame(self.root, corner_radius=16)
        actions.grid(row=2, column=0, padx=18, pady=8, sticky="ew")
        for index in range(6):
            actions.grid_columnconfigure(index, weight=1)

        self.start_button = ctk.CTkButton(actions, text="启动 WebUI", command=self.start_webui)
        self.start_button.grid(row=0, column=0, padx=8, pady=12, sticky="ew")
        self.browser_button = ctk.CTkButton(actions, text="打开浏览器", command=self.open_browser)
        self.browser_button.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.stop_button = ctk.CTkButton(actions, text="停止服务", command=self.stop_webui)
        self.stop_button.grid(row=0, column=2, padx=8, pady=12, sticky="ew")
        self.reinstall_button = ctk.CTkButton(actions, text="重装依赖", command=lambda: self.start_webui(reinstall=True))
        self.reinstall_button.grid(row=0, column=3, padx=8, pady=12, sticky="ew")
        self.logs_button = ctk.CTkButton(actions, text="打开日志", command=self.open_logs_folder)
        self.logs_button.grid(row=0, column=4, padx=8, pady=12, sticky="ew")
        self.folder_button = ctk.CTkButton(actions, text="项目文件夹", command=self.open_project_folder)
        self.folder_button.grid(row=0, column=5, padx=8, pady=12, sticky="ew")

        log_frame = ctk.CTkFrame(self.root, corner_radius=16)
        log_frame.grid(row=3, column=0, padx=18, pady=8, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(log_frame, text="运行日志 / Runtime Log", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(14, 6), sticky="w"
        )
        self.log_text = ctk.CTkTextbox(log_frame, wrap="word")
        self.log_text.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

        footer = ctk.CTkLabel(self.root, text=DISCLAIMER, wraplength=780, justify="left")
        footer.grid(row=4, column=0, padx=20, pady=(4, 16), sticky="ew")

    def _build_tkinter_ui(self) -> None:
        self.root.configure(bg="#f3f5f8")

        frame = ctk.Frame(self.root, bg="#f3f5f8")
        frame.pack(fill=BOTH, expand=True, padx=18, pady=18)

        ctk.Label(frame, text=APP_TITLE, font=("Arial", 22, "bold"), bg="#f3f5f8").pack(anchor="w")
        ctk.Label(frame, text=APP_SUBTITLE, font=("Arial", 11), bg="#f3f5f8").pack(anchor="w", pady=(2, 16))

        status_row = ctk.Frame(frame, bg="#f3f5f8")
        status_row.pack(fill=X, pady=(0, 10))
        self.status_dot = ctk.Label(status_row, text="●", font=("Arial", 18), bg="#f3f5f8")
        self.status_dot.pack(side=LEFT)
        self.status_label = ctk.Label(status_row, text="未启动", font=("Arial", 12, "bold"), bg="#f3f5f8")
        self.status_label.pack(side=LEFT, padx=6)
        self.url_label = ctk.Label(status_row, text=self.current_url, bg="#f3f5f8")
        self.url_label.pack(side=RIGHT)

        button_row = ctk.Frame(frame, bg="#f3f5f8")
        button_row.pack(fill=X, pady=(0, 12))
        self.start_button = ctk.Button(button_row, text="启动 WebUI", command=self.start_webui)
        self.start_button.pack(side=LEFT, padx=4)
        self.browser_button = ctk.Button(button_row, text="打开浏览器", command=self.open_browser)
        self.browser_button.pack(side=LEFT, padx=4)
        self.stop_button = ctk.Button(button_row, text="停止服务", command=self.stop_webui)
        self.stop_button.pack(side=LEFT, padx=4)
        self.reinstall_button = ctk.Button(button_row, text="重装依赖", command=lambda: self.start_webui(reinstall=True))
        self.reinstall_button.pack(side=LEFT, padx=4)
        self.logs_button = ctk.Button(button_row, text="打开日志", command=self.open_logs_folder)
        self.logs_button.pack(side=LEFT, padx=4)
        self.folder_button = ctk.Button(button_row, text="项目文件夹", command=self.open_project_folder)
        self.folder_button.pack(side=LEFT, padx=4)

        self.log_text = ctk.Text(frame, wrap="word", height=22)
        self.log_text.pack(fill=BOTH, expand=True)
        ctk.Label(frame, text=DISCLAIMER, bg="#f3f5f8", wraplength=780, justify="left").pack(anchor="w", pady=(10, 0))

    # ---------- UI helpers ----------
    def _set_status(self, text: str, color: str) -> None:
        self.status_label.configure(text=text)
        if HAS_CUSTOMTKINTER:
            self.status_dot.configure(text_color=color)
        else:
            self.status_dot.configure(fg=color)

    def _append_log(self, message: str) -> None:
        self.log_queue.put(message)

    def _drain_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_text.insert(END, message + "\n")
            self.log_text.see(END)
        self.root.after(120, self._drain_log_queue)

    def _set_buttons_running(self, running: bool) -> None:
        if HAS_CUSTOMTKINTER:
            self.start_button.configure(state="disabled" if running else "normal")
            self.reinstall_button.configure(state="disabled" if running else "normal")
            self.stop_button.configure(state="normal" if running else "disabled")
        else:
            self.start_button.configure(state="disabled" if running else "normal")
            self.reinstall_button.configure(state="disabled" if running else "normal")
            self.stop_button.configure(state="normal" if running else "disabled")

    # ---------- actions ----------
    def start_webui(self, reinstall: bool = False) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(APP_TITLE, "启动流程正在进行中，请稍等。")
            return
        if self.launcher and self.launcher.is_running():
            self.open_browser()
            return

        self._set_status("正在启动", "orange")
        self._set_buttons_running(True)

        self.worker = threading.Thread(target=self._start_worker, args=(reinstall,), daemon=True)
        self.worker.start()

    def _start_worker(self, reinstall: bool) -> None:
        try:
            config = LauncherConfig(
                project_root=self.project_root,
                force_reinstall=reinstall,
                allow_port_fallback=True,
                auto_open_browser=True,
            )
            self.launcher = LocalWebUILauncher(config, log_callback=self._append_log)
            app_python = self.launcher.prepare_environment()
            self.current_url = self.launcher.start_server(app_python)
            self.launcher.wait_until_ready()
            self.launcher.open_browser()
            self.root.after(0, lambda: self.url_label.configure(text=self.current_url))
            self.root.after(0, lambda: self._set_status("已运行", "green"))
        except LauncherError as exc:
            self._append_log(f"启动失败：{exc}")
            self.root.after(0, lambda: self._set_status("启动失败", "red"))
            self.root.after(0, lambda: messagebox.showerror(APP_TITLE, f"启动失败：\n{exc}"))
            self.root.after(0, lambda: self._set_buttons_running(False))
        except Exception as exc:  # noqa: BLE001 - GUI should not crash on user machines.
            self._append_log(f"未知错误：{type(exc).__name__}: {exc}")
            self.root.after(0, lambda: self._set_status("启动失败", "red"))
            self.root.after(0, lambda: messagebox.showerror(APP_TITLE, f"未知错误：\n{type(exc).__name__}: {exc}"))
            self.root.after(0, lambda: self._set_buttons_running(False))

    def stop_webui(self) -> None:
        if self.launcher:
            self.launcher.stop_server()
        self._set_status("已停止", "gray")
        self._set_buttons_running(False)

    def open_browser(self) -> None:
        if self.launcher and self.launcher.is_running():
            self.launcher.open_browser()
        else:
            import webbrowser

            webbrowser.open(self.current_url)

    def _open_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True) if path.suffix == "" else path.parent.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(path)])
        elif sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def open_logs_folder(self) -> None:
        self._open_path(self.project_root / "logs")

    def open_project_folder(self) -> None:
        self._open_path(self.project_root)

    def on_close(self) -> None:
        if self.launcher and self.launcher.is_running():
            if not messagebox.askyesno(APP_TITLE, "WebUI 仍在运行。是否停止服务并退出？"):
                return
            self.launcher.stop_server()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    try:
        LauncherGUI().run()
    except LauncherError as exc:
        messagebox.showerror(APP_TITLE, f"无法启动 GUI：\n{exc}")
        raise SystemExit(1) from exc
