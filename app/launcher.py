
#!/usr/bin/env python3
"""Local AI Lab desktop launcher for Ubuntu."""

import os
import shlex
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen
import json


PROJECT = Path("/mnt/Experiment/local-ai-lab")
AI_LAB = Path("/mnt/Experiment/AI-Lab")
OLLAMA = AI_LAB / "runtime" / "bin" / "ollama"
MODELS_DIR = AI_LAB / "models"
HOST = "127.0.0.1"
PORT = 11434
API = f"http://{HOST}:{PORT}"

BG = "#0b1020"
PANEL = "#131b2e"
PANEL_ALT = "#19243a"
FG = "#edf2ff"
MUTED = "#91a1bd"
ACCENT = "#7c9cff"
GREEN = "#5ee0a0"
RED = "#ff7b88"


class LocalAILab:
    def __init__(self, root):
        self.root = root
        self.server_process = None
        self.models = []
        self.model_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Checking runtime...")
        self.detail_var = tk.StringVar(value="Loading installed models...")
        self._closing = False

        self.root.title("Local AI Lab")
        self.root.geometry("900x650")
        self.root.minsize(720, 540)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._setup_theme()
        self._build_ui()
        self.refresh()

        # Refresh the runtime status and model list periodically.
        self.root.after(5000, self.auto_refresh)

    def _setup_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_ALT,
            background=PANEL_ALT,
            foreground=FG,
            arrowcolor=FG,
            padding=8,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_ALT)],
            foreground=[("readonly", FG)],
        )

    def _label(self, parent, text, size=10, color=FG, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=("DejaVu Sans", size, "bold" if bold else "normal"),
            anchor="w",
        )

    def _button(self, parent, text, command, primary=False):
        bg = ACCENT if primary else PANEL_ALT
        fg = BG if primary else FG
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground="#9bb4ff" if primary else "#263654",
            activeforeground=BG if primary else FG,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2",
            font=("DejaVu Sans", 10, "bold"),
        )

    def _card(self, parent):
        return tk.Frame(parent, bg=PANEL, padx=20, pady=18)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG, padx=28, pady=24)
        header.pack(fill="x")

        tk.Label(
            header,
            text="LOCAL AI LAB",
            bg=BG,
            fg=FG,
            font=("DejaVu Sans", 23, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Your local models. One launch point.",
            bg=BG,
            fg=MUTED,
            font=("DejaVu Sans", 10),
        ).pack(anchor="w", pady=(5, 0))

        self.status_label = tk.Label(
            header,
            textvariable=self.status_var,
            bg=BG,
            fg=MUTED,
            font=("DejaVu Sans", 10, "bold"),
        )
        self.status_label.pack(anchor="w", pady=(14, 0))

        body = tk.Frame(self.root, bg=BG, padx=28, pady=4)
        body.pack(fill="both", expand=True)

        # Quick launch card
        launch = self._card(body)
        launch.pack(fill="x", pady=(0, 14))

        self._label(launch, "QUICK LAUNCH", 10, ACCENT, True).pack(
            anchor="w"
        )
        self._label(launch, "Choose a model", 15, FG, True).pack(
            anchor="w", pady=(8, 10)
        )

        self.model_box = ttk.Combobox(
            launch,
            textvariable=self.model_var,
            state="readonly",
            font=("DejaVu Sans", 10),
        )
        self.model_box.pack(fill="x", pady=(0, 12))

        actions = tk.Frame(launch, bg=PANEL)
        actions.pack(fill="x")

        self._button(
            actions, "▶  Launch Chat", self.launch_model, True
        ).pack(side="left")

        self._button(
            actions, "↻  Refresh Models", self.refresh
        ).pack(side="left", padx=(10, 0))

        # Runtime card
        runtime = self._card(body)
        runtime.pack(fill="x", pady=(0, 14))

        self._label(runtime, "OLLAMA RUNTIME", 10, ACCENT, True).pack(
            anchor="w"
        )
        self._label(
            runtime, "Manage the local inference server", 13, FG, True
        ).pack(anchor="w", pady=(8, 12))

        runtime_actions = tk.Frame(runtime, bg=PANEL)
        runtime_actions.pack(fill="x")

        self._button(
            runtime_actions, "Start Server", self.start_server, True
        ).pack(side="left")

        self._button(
            runtime_actions, "Stop Managed Server", self.stop_server
        ).pack(side="left", padx=(10, 0))

        self._button(
            runtime_actions, "Diagnostics", self.show_diagnostics
        ).pack(side="left", padx=(10, 0))

        # Footer / paths
        footer = self._card(body)
        footer.pack(fill="x")

        self._label(footer, "ENVIRONMENT", 10, ACCENT, True).pack(
            anchor="w"
        )

        self._label(
            footer, f"Project  ·  {PROJECT}", 9, MUTED
        ).pack(anchor="w", pady=(8, 3))

        self._label(
            footer, f"Runtime  ·  {OLLAMA}", 9, MUTED
        ).pack(anchor="w", pady=3)

        self._label(
            footer, f"Models  ·  {MODELS_DIR}", 9, MUTED
        ).pack(anchor="w", pady=3)

        bottom = tk.Frame(self.root, bg=BG, padx=28, pady=12)
        bottom.pack(fill="x", side="bottom")

        self._label(
            bottom,
            "LOCAL AI LAB  /  UBUNTU",
            8,
            MUTED,
        ).pack(side="left")

        self._label(
            bottom,
            "Local inference · No cloud API required",
            8,
            MUTED,
        ).pack(side="right")

    def _environment(self):
        env = os.environ.copy()
        env["OLLAMA_HOST"] = API
        env["OLLAMA_MODELS"] = str(MODELS_DIR)
        return env

    def _request(self, endpoint="/api/tags", timeout=2):
        request = Request(API + endpoint)
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def server_running(self):
        try:
            self._request("/api/tags", timeout=1)
            return True
        except (URLError, OSError, TimeoutError, ValueError):
            return False

    def refresh(self):
        if not OLLAMA.is_file():
            self.status_var.set("● Runtime not found")
            self.status_label.configure(fg=RED)
            self.detail_var.set(f"Missing executable: {OLLAMA}")
            self.models = []
            self.model_box["values"] = []
            return

        if not MODELS_DIR.is_dir():
            self.status_var.set("● Model directory not found")
            self.status_label.configure(fg=RED)
            self.models = []
            self.model_box["values"] = []
            return

        if not self.server_running():
            self.status_var.set("● Server offline")
            self.status_label.configure(fg=RED)
            self.detail_var.set("Start the Ollama server to load models.")
            self.models = []
            self.model_box["values"] = []
            return

        try:
            data = self._request("/api/tags")
            self.models = data.get("models", [])
            names = [item["name"] for item in self.models]

            self.model_box["values"] = names
            if names:
                current = self.model_var.get()
                if current not in names:
                    preferred = "qwen2.5-coder:7b"
                    self.model_var.set(
                        preferred if preferred in names else names[0]
                    )
                self.status_var.set("● Ollama online")
                self.status_label.configure(fg=GREEN)
                self.detail_var.set(f"{len(names)} installed model(s)")
            else:
                self.model_var.set("")
                self.status_var.set("● Server online · No models")
                self.status_label.configure(fg=ACCENT)
                self.detail_var.set("Install or import a model first.")

        except (URLError, OSError, ValueError) as exc:
            self.status_var.set("● Could not read model list")
            self.status_label.configure(fg=RED)
            self.detail_var.set(str(exc))

    def start_server(self):
        if self.server_running():
            messagebox.showinfo(
                "Ollama", "The Ollama server is already responding."
            )
            self.refresh()
            return

        if not OLLAMA.is_file():
            messagebox.showerror(
                "Runtime missing", f"Cannot find Ollama:\n{OLLAMA}"
            )
            return

        try:
            log_path = Path("/tmp/local-ai-lab-ollama.log")
            log_file = open(log_path, "a", encoding="utf-8")

            self.server_process = subprocess.Popen(
                [str(OLLAMA), "serve"],
                env=self._environment(),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            # The server process retains its log descriptor.
            log_file.close()

            self.status_var.set("● Starting Ollama...")
            self.status_label.configure(fg=ACCENT)
            self.root.after(1200, self.wait_for_server)

        except OSError as exc:
            messagebox.showerror("Could not start Ollama", str(exc))

    def wait_for_server(self, attempts=12):
        if self.server_running():
            self.refresh()
            return

        if attempts <= 0:
            self.status_var.set("● Server startup failed")
            self.status_label.configure(fg=RED)
            messagebox.showerror(
                "Ollama startup failed",
                "Check /tmp/local-ai-lab-ollama.log\n\n"
                "Also verify that port 11434 is available.",
            )
            return

        self.root.after(1000, lambda: self.wait_for_server(attempts - 1))

    def stop_server(self):
        if not self.server_running():
            self.refresh()
            return

        if self.server_process is None:
            messagebox.showinfo(
                "Ollama",
                "This server was not started by this GUI.\n"
                "It has been left running to avoid interrupting "
                "another application.",
            )
            return

        if self.server_process.poll() is not None:
            self.server_process = None
            self.refresh()
            return

        if not messagebox.askyesno(
            "Stop Ollama?",
            "Stopping Ollama interrupts active model sessions.\n"
            "Do you want to continue?",
        ):
            return

        self.server_process.terminate()
        try:
            self.server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server_process.kill()
            self.server_process.wait(timeout=2)

        self.server_process = None
        self.refresh()

    def launch_model(self):
        model = self.model_var.get().strip()
        if not model:
            messagebox.showwarning(
                "No model selected", "Refresh the model list first."
            )
            return

        if not self.server_running():
            if not messagebox.askyesno(
                "Start Ollama?",
                "The server is offline. Start it now?",
            ):
                return
            self.start_server()
            self.root.after(1500, lambda: self.launch_when_ready(model))
            return

        self._open_chat_terminal(model)


    def launch_when_ready(self, model, attempts=12):
        if self.server_running():
            self.refresh()
            self._open_chat_terminal(model)
            return

        if attempts <= 0:
            messagebox.showerror(
                "Ollama not ready",
                "The server did not become ready.\n"
                "Check /tmp/local-ai-lab-ollama.log",
            )
            return

        self.root.after(
            1000,
            lambda: self.launch_when_ready(model, attempts - 1),
        )


    def _open_chat_terminal(self, model):
        terminal = shutil.which("x-terminal-emulator")
        if not terminal:
            messagebox.showerror(
                "Terminal not found",
                "Install or configure an Ubuntu terminal emulator.",
            )
            return

        command = (
            f"export OLLAMA_HOST={shlex.quote(API)}; "
            f"{shlex.quote(str(OLLAMA))} run {shlex.quote(model)}; "
            "result=$?; "
            "echo; "
            "echo 'Chat session ended.'; "
            "echo 'Close this window when finished.'; "
            "read -r -p 'Press Enter to close...'; "
            "exit $result"
        )

        try:
            subprocess.Popen(
                [terminal, "-e", "bash", "-lc", command],
                env=self._environment(),
                start_new_session=True,
            )
        except OSError as exc:
            messagebox.showerror("Could not launch chat", str(exc))

    def show_diagnostics(self):
        running = self.server_running()
        models_count = len(self.models)

        text = (
            f"Project: {PROJECT}\n"
            f"Ollama executable: {OLLAMA}\n"
            f"Executable exists: {OLLAMA.is_file()}\n"
            f"Models directory: {MODELS_DIR}\n"
            f"Models directory exists: {MODELS_DIR.is_dir()}\n"
            f"API endpoint: {API}\n"
            f"Server responding: {running}\n"
            f"Models loaded in UI: {models_count}\n"
            f"GUI-managed process: "
            f"{self.server_process is not None}\n"
            f"Server log: /tmp/local-ai-lab-ollama.log\n"
        )

        if running:
            try:
                data = self._request("/api/tags")
                text += "\nInstalled models:\n"
                for item in data.get("models", []):
                    text += f"  • {item.get('name', 'unknown')}\n"
            except (URLError, OSError, ValueError):
                pass

        window = tk.Toplevel(self.root)
        window.title("Local AI Lab Diagnostics")
        window.geometry("680x420")
        window.configure(bg=BG)

        output = tk.Text(
            window,
            bg=PANEL,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            padx=16,
            pady=16,
            font=("DejaVu Sans Mono", 10),
            wrap="word",
        )
        output.pack(fill="both", expand=True, padx=14, pady=14)
        output.insert("1.0", text)
        output.configure(state="disabled")

    def auto_refresh(self):
        if self._closing:
            return
        self.refresh()
        self.root.after(5000, self.auto_refresh)

    def close(self):
        if self.server_process and self.server_process.poll() is None:
            answer = messagebox.askyesnocancel(
                "Close Local AI Lab",
                "The GUI started an Ollama server.\n\n"
                "Yes: stop the server and close.\n"
                "No: leave the server running and close.\n"
                "Cancel: keep the GUI open.",
            )
            if answer is None:
                return
            if answer:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
        self._closing = True
        self.root.destroy()


def main():
    root = tk.Tk()
    LocalAILab(root)
    root.mainloop()


if __name__ == "__main__":
    main()
