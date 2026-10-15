
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
import signal
import time


PROJECT = Path("/mnt/All/LLM-Exp/local-ai-lab")
AI_LAB = Path("/mnt/All/LLM-Exp")
OLLAMA = AI_LAB / "runtime" / "bin" / "ollama"
MODELS_DIR = AI_LAB / "models"
HOST = "127.0.0.1"
PORT = 11434
API = f"http://{HOST}:{PORT}"

BG = "#080c16"
PANEL = "#101827"
PANEL_ALT = "#19253a"
FG = "#edf5ff"
MUTED = "#91a3bd"
ACCENT = "#54e6d0"
GREEN = "#5ee6a8"
RED = "#ff7189"


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
        self.root.geometry("960x780")
        self.root.minsize(640, 480)
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
            arrowcolor="#54e6d0",
            padding=10,
            borderwidth=0,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_ALT)],
            foreground=[("readonly", FG)],
            selectbackground=[("readonly", PANEL_ALT)],
            selectforeground=[("readonly", FG)],
        )
        style.configure(
            "GPU.Horizontal.TProgressbar",
            troughcolor=PANEL_ALT,
            background=ACCENT,
            bordercolor=PANEL,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=9,
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
        return tk.Frame(
            parent,
            bg=PANEL,
            padx=20,
            pady=18,
            highlightbackground="#26364d",
            highlightthickness=1,
            bd=0,
        )

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG, padx=30, pady=23)
        header.pack(fill="x")

        brand = tk.Frame(header, bg=BG)
        brand.pack(fill="x")

        mark = tk.Label(
            brand, text="◈", bg=BG, fg="#54e6d0",
            font=("DejaVu Sans", 29, "bold"),
        )
        mark.pack(side="left", padx=(0, 12))

        titles = tk.Frame(brand, bg=BG)
        titles.pack(side="left", fill="x", expand=True)

        tk.Label(
            titles, text="LOCAL AI LAB", bg=BG, fg=FG,
            font=("DejaVu Sans", 21, "bold"),
        ).pack(anchor="w")

        tk.Label(
            titles, text="PRIVATE INFERENCE WORKSTATION",
            bg=BG, fg="#54e6d0",
            font=("DejaVu Sans", 8, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        self.status_label = tk.Label(
            header, textvariable=self.status_var,
            bg=BG, fg=MUTED,
            font=("DejaVu Sans", 10, "bold"),
        )
        self.status_label.pack(anchor="w", pady=(17, 0))

        tk.Frame(self.root, bg="#263752", height=1).pack(fill="x")

        # Scrollable dashboard; header and bottom bar stay visible.
        body_shell = tk.Frame(self.root, bg=BG)
        body_shell.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            body_shell, bg=BG, highlightthickness=0, borderwidth=0
        )
        scrollbar = ttk.Scrollbar(
            body_shell, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=BG, padx=30, pady=22)
        body_window = canvas.create_window(
            (0, 0), window=body, anchor="nw"
        )

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_body(event):
            canvas.itemconfigure(body_window, width=event.width)

        body.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", resize_body)

        def scroll_dashboard(event):
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")
            elif event.delta:
                canvas.yview_scroll(-int(event.delta / 120), "units")

        def on_mousewheel(event):
            if event.widget.winfo_toplevel() is self.root:
                scroll_dashboard(event)

        self.root.bind_all("<MouseWheel>", on_mousewheel)
        self.root.bind_all("<Button-4>", on_mousewheel)
        self.root.bind_all("<Button-5>", on_mousewheel)

        # Model workspace
        launch = self._card(body)
        launch.pack(fill="x", pady=(0, 14))

        self._label(
            launch, "MODEL WORKSPACE", 9, "#54e6d0", True
        ).pack(anchor="w")

        self._label(
            launch, "Choose your intelligence", 17, FG, True
        ).pack(anchor="w", pady=(8, 4))

        self._label(
            launch, "Select an installed model to begin a local session.",
            9, MUTED,
        ).pack(anchor="w", pady=(0, 15))

        self.model_box = ttk.Combobox(
            launch, textvariable=self.model_var,
            state="readonly", font=("DejaVu Sans", 10),
        )
        self.model_box.pack(fill="x")
        self.model_box.bind(
            "<<ComboboxSelected>>", self._selected_model_changed
        )

        self.model_detail_var = tk.StringVar(
            value="Model metadata will appear here."
        )
        tk.Label(
            launch, textvariable=self.model_detail_var,
            bg=PANEL, fg="#a8b9d5",
            font=("DejaVu Sans", 9), anchor="w",
        ).pack(fill="x", pady=(9, 16))

        actions = tk.Frame(launch, bg=PANEL)
        actions.pack(fill="x")

        self._button(
            actions, "▶  Launch Chat", self.launch_model, True
        ).pack(side="left")

        self._button(
            actions, "↻  Refresh Models", self.refresh
        ).pack(side="left", padx=(10, 0))

        # Runtime controls
        runtime = self._card(body)
        runtime.pack(fill="x", pady=(0, 14))

        self._label(
            runtime, "INFERENCE ENGINE", 9, "#54e6d0", True
        ).pack(anchor="w")

        self._label(
            runtime, "Ollama runtime", 15, FG, True
        ).pack(anchor="w", pady=(8, 4))

        self._label(
            runtime, "Start the local server only when you need it.",
            9, MUTED,
        ).pack(anchor="w", pady=(0, 14))

        runtime_actions = tk.Frame(runtime, bg=PANEL)
        runtime_actions.pack(fill="x")

        self._button(
            runtime_actions, "Start Server",
            self.start_server, True,
        ).pack(side="left")

        self._button(
            runtime_actions, "Stop Managed Server",
            self.stop_server,
        ).pack(side="left", padx=(10, 0))

        self._button(
            runtime_actions, "Diagnostics",
            self.show_diagnostics,
        ).pack(side="left", padx=(10, 0))

        # Live hardware information
        monitor = self._card(body)
        monitor.pack(fill="x", pady=(0, 14))

        self._label(
            monitor, "HARDWARE TELEMETRY",
            9, ACCENT, True,
        ).pack(anchor="w")

        self.gpu_name_var = tk.StringVar(
            value="Detecting NVIDIA GPU..."
        )
        tk.Label(
            monitor,
            textvariable=self.gpu_name_var,
            bg=PANEL,
            fg=FG,
            anchor="w",
            font=("DejaVu Sans", 11, "bold"),
        ).pack(fill="x", pady=(8, 14))

        metrics = tk.Frame(monitor, bg=PANEL)
        metrics.pack(fill="x")

        gpu_metric = tk.Frame(
            metrics, bg=PANEL_ALT, padx=14, pady=12
        )
        gpu_metric.pack(
            side="left", fill="both", expand=True, padx=(0, 6)
        )

        self._label(
            gpu_metric, "GPU UTILIZATION", 8, ACCENT, True
        ).pack(anchor="w")

        self.gpu_util_var = tk.StringVar(value="—")
        tk.Label(
            gpu_metric,
            textvariable=self.gpu_util_var,
            bg=PANEL_ALT,
            fg=FG,
            font=("DejaVu Sans", 18, "bold"),
        ).pack(anchor="w", pady=(5, 9))

        self.gpu_util_bar = ttk.Progressbar(
            gpu_metric,
            maximum=100,
            mode="determinate",
            style="GPU.Horizontal.TProgressbar",
        )
        self.gpu_util_bar.pack(fill="x")

        vram_metric = tk.Frame(
            metrics, bg=PANEL_ALT, padx=14, pady=12
        )
        vram_metric.pack(
            side="left", fill="both", expand=True, padx=(6, 0)
        )

        self._label(
            vram_metric, "DEDICATED VRAM", 8, ACCENT, True
        ).pack(anchor="w")

        self.vram_var = tk.StringVar(value="—")
        tk.Label(
            vram_metric,
            textvariable=self.vram_var,
            bg=PANEL_ALT,
            fg=FG,
            font=("DejaVu Sans", 14, "bold"),
        ).pack(anchor="w", pady=(8, 12))

        self.vram_bar = ttk.Progressbar(
            vram_metric,
            maximum=100,
            mode="determinate",
            style="GPU.Horizontal.TProgressbar",
        )
        self.vram_bar.pack(fill="x")

        ram_metric = tk.Frame(
            metrics, bg=PANEL_ALT, padx=14, pady=12
        )
        ram_metric.pack(
            side="left", fill="both", expand=True, padx=(6, 0)
        )

        self._label(
            ram_metric, "SYSTEM RAM", 8, ACCENT, True
        ).pack(anchor="w")

        self.ram_var = tk.StringVar(value="Reading memory...")
        tk.Label(
            ram_metric,
            textvariable=self.ram_var,
            bg=PANEL_ALT,
            fg=FG,
            font=("DejaVu Sans", 12, "bold"),
        ).pack(anchor="w", pady=(8, 12))

        self.ram_bar = ttk.Progressbar(
            ram_metric,
            maximum=100,
            mode="determinate",
            style="GPU.Horizontal.TProgressbar",
        )
        self.ram_bar.pack(fill="x")

        self._label(
            monitor, f"LOCAL API  ·  {API}", 9, MUTED
        ).pack(anchor="w", pady=(12, 0))

        # Environment footer
        footer = tk.Frame(body, bg=BG)
        footer.pack(fill="x", pady=(1, 0))

        self._label(
            footer, "ENVIRONMENT", 8, "#54e6d0", True
        ).pack(anchor="w", pady=(0, 7))

        self._label(
            footer, f"PROJECT  /  {PROJECT}", 8, MUTED
        ).pack(anchor="w", pady=2)

        self._label(
            footer, f"RUNTIME  /  {OLLAMA}", 8, MUTED
        ).pack(anchor="w", pady=2)

        self._label(
            footer, f"MODELS  /  {MODELS_DIR}", 8, MUTED
        ).pack(anchor="w", pady=2)

        bottom = tk.Frame(self.root, bg="#080d18", padx=30, pady=10)
        bottom.pack(fill="x", side="bottom")

        self._label(
            bottom, "LOCAL AI LAB  /  UBUNTU",
            8, MUTED,
        ).pack(side="left")

        self._label(
            bottom, "LOCAL-FIRST  ·  PRIVATE BY DESIGN",
            8, "#54e6d0", True,
        ).pack(side="right")

    def _selected_model_changed(self, _event=None):
        name = self.model_var.get().strip()
        model = next(
            (item for item in self.models if item.get("name") == name),
            None,
        )
        if not model:
            self.model_detail_var.set(
                "Model metadata appears when the server is online."
            )
            return

        size = model.get("size")
        if isinstance(size, (int, float)) and size > 0:
            size_text = f"{size / (1024 ** 3):.2f} GiB"
        else:
            size_text = "Size unavailable"

        details = model.get("details") or {}
        parts = [size_text]
        for key in ("family", "parameter_size", "quantization_level"):
            value = details.get(key)
            if value:
                parts.append(str(value))
        self.model_detail_var.set("   ·   ".join(parts))

    def _update_ram_status(self):
        try:
            memory = {}
            with open("/proc/meminfo", encoding="utf-8") as info:
                for line in info:
                    key, value = line.split(":", 1)
                    if key in ("MemTotal", "MemAvailable"):
                        memory[key] = int(value.strip().split()[0])

            total_kib = memory["MemTotal"]
            available_kib = memory["MemAvailable"]
            used_kib = total_kib - available_kib
            percent = 100 * used_kib / total_kib if total_kib else 0

            self.ram_var.set(
                f"{used_kib / 1048576:.1f} / "
                f"{total_kib / 1048576:.1f} GiB  ·  {percent:.0f}%"
            )
            self.ram_bar.configure(
                value=max(0, min(100, percent))
            )
        except (OSError, KeyError, ValueError):
            self.ram_var.set("RAM information unavailable")
            self.ram_bar.configure(value=0)

    def _update_gpu_status(self):
        self._update_ram_status()

        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
                check=True,
            )
            line = result.stdout.strip().splitlines()[0]
            name, used, total, utilization = [
                part.strip() for part in line.split(",", 3)
            ]

            used_mib = float(used)
            total_mib = float(total)
            vram_percent = (
                100 * used_mib / total_mib if total_mib > 0 else 0
            )

            self.gpu_name_var.set(name)
            self.vram_var.set(
                f"{used_mib:.0f} / {total_mib:.0f} MiB"
                f"  ·  {vram_percent:.0f}%"
            )
            self.vram_bar.configure(
                value=max(0, min(100, vram_percent))
            )

            try:
                gpu_percent = float(utilization)
                self.gpu_util_var.set(f"{gpu_percent:.0f}%")
                self.gpu_util_bar.configure(
                    value=max(0, min(100, gpu_percent))
                )
            except ValueError:
                self.gpu_util_var.set("Unavailable")
                self.gpu_util_bar.configure(value=0)
            self.vram_bar.configure(
                value=max(0, min(100, vram_percent))
            )
        except (
            FileNotFoundError, subprocess.SubprocessError,
            OSError, IndexError, ValueError,
        ):
            self.gpu_name_var.set("GPU telemetry unavailable")
            self.gpu_util_var.set("Unavailable")
            self.vram_var.set("Unable to read VRAM")
            self.gpu_util_bar.configure(value=0)
            self.vram_bar.configure(value=0)

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

    def find_ollama_server_pid(self):
        """Find a running server using this lab's exact Ollama executable."""
        expected = os.fsencode(str(OLLAMA))

        try:
            proc_entries = os.listdir("/proc")
        except OSError:
            return None

        for entry in proc_entries:
            if not entry.isdigit():
                continue

            pid = int(entry)

            try:
                with open(f"/proc/{pid}/cmdline", "rb") as cmd_file:
                    args = cmd_file.read().split(b"\0")

                args = [arg for arg in args if arg]
                if len(args) < 2:
                    continue

                if args[0] != expected or args[1] != b"serve":
                    continue

                # Verify that the PID still belongs to this executable.
                with open(f"/proc/{pid}/exe", "rb") as exe_file:
                    executable = os.readlink(f"/proc/{pid}/exe")

                if os.path.realpath(executable) == os.path.realpath(OLLAMA):
                    return pid

            except (OSError, ProcessLookupError, PermissionError):
                continue

        return None

    def is_local_ollama_server(self, pid):
        """Verify that a PID still runs this lab's Ollama server."""
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as cmd_file:
                args = [arg for arg in cmd_file.read().split(b"\0") if arg]

            if len(args) < 2:
                return False

            if args[0] != os.fsencode(str(OLLAMA)) or args[1] != b"serve":
                return False

            executable = os.readlink(f"/proc/{pid}/exe")
            return os.path.realpath(executable) == os.path.realpath(OLLAMA)

        except (OSError, ProcessLookupError, PermissionError):
            return False

    def terminate_local_ollama(self, pid):
        """Stop only a verified Local AI Lab Ollama server."""
        if not self.is_local_ollama_server(pid):
            return False

        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if not self.is_local_ollama_server(pid):
                return True
            time.sleep(0.1)

        # Re-verify the process before attempting a forced stop.
        if self.is_local_ollama_server(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                return True

        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if not self.is_local_ollama_server(pid):
                return True
            time.sleep(0.1)

        return not self.is_local_ollama_server(pid)

    def refresh(self):
        self._update_gpu_status()
        if not OLLAMA.is_file():
            self.status_var.set("● Runtime not found")
            self.status_label.configure(fg=RED)
            self.detail_var.set(f"Missing executable: {OLLAMA}")
            self.models = []
            self._selected_model_changed()
            self.model_box["values"] = []
            return

        if not MODELS_DIR.is_dir():
            self.status_var.set("● Model directory not found")
            self.status_label.configure(fg=RED)
            self.models = []
            self._selected_model_changed()
            self.model_box["values"] = []
            return

        if not self.server_running():
            self.status_var.set("● Server offline")
            self.status_label.configure(fg=RED)
            self.detail_var.set("Start the Ollama server to load models.")
            self.models = []
            self._selected_model_changed()
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
                self._selected_model_changed()
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

        pid = self.find_ollama_server_pid()
        if pid is None:
            messagebox.showwarning(
                "Ollama not verified",
                "A server is responding, but its process could not be "
                "verified as this Local AI Lab runtime. It has not been stopped.",
            )
            return

        if not messagebox.askyesno(
            "Stop Ollama?",
            "Stopping Ollama interrupts active model sessions.\n\n"
            "Do you want to stop the verified Local AI Lab server?",
        ):
            return

        if not self.terminate_local_ollama(pid):
            messagebox.showerror(
                "Could not stop Ollama",
                "The server could not be confirmed as stopped. "
                "Check the process and try again.",
            )
            return

        if self.server_process and self.server_process.pid == pid:
            try:
                self.server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass

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

        # Use a short, readable title while retaining the full model ID.
        title = model.split(":", 1)[0].split(".", 1)[0].lower()
        safe_title = shlex.quote(title)

        command = (
            f"printf '\\033]0;{title}\\007'; "
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
                [terminal, "--title", title, "-e", "bash", "-lc", command],
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
        pid = self.find_ollama_server_pid()

        if self.server_running():
            if pid is None:
                messagebox.showwarning(
                    "Ollama not verified",
                    "A server is responding, but its process could not be "
                    "verified as this Local AI Lab runtime. The GUI will "
                    "remain open so the server is not stopped accidentally.",
                )
                return

            answer = messagebox.askyesno(
                "Close Local AI Lab",
                "A Local AI Lab Ollama server is running.\n\n"
                "Yes: stop the server and close Local AI Lab.\n"
                "No: keep Local AI Lab open.",
            )
            if not answer:
                return

            if not self.terminate_local_ollama(pid):
                messagebox.showerror(
                    "Could not stop Ollama",
                    "The server could not be confirmed as stopped. "
                    "Local AI Lab will remain open.",
                )
                return

            if self.server_process and self.server_process.pid == pid:
                try:
                    self.server_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass

            self.server_process = None

        self._closing = True
        self.root.destroy()


def main():
    root = tk.Tk()
    LocalAILab(root)
    root.mainloop()


if __name__ == "__main__":
    main()
