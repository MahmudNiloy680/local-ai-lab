# Local AI Lab

A local-first AI workspace for running language models on Ubuntu. Local AI Lab combines a lightweight desktop launcher with an isolated Ollama runtime and model storage, keeping the application source separate from large model files and runtime binaries.

> **Project status:** Active development. The desktop launcher and launch-path integration are in place; complete end-to-end validation and further UI polish remain in progress.

## Overview

The project is designed around a few principles:

- **Local-first:** run supported language models on your own machine.
- **Separation of concerns:** keep source code, the Ollama runtime, and model data in separate locations.
- **Simple launch workflow:** open the desktop application with `ai-lab`.
- **GPU-aware:** use available NVIDIA GPU acceleration when supported by the installed Ollama runtime and model.
- **Maintainable source:** keep runtime binaries and model weights out of Git.

## Current environment

The original development environment is:

- **OS:** Ubuntu 26.04.1 LTS
- **Laptop:** Lenovo LOQ 15IRX9
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU, 6 GB VRAM
- **Runtime:** Ollama
- **Primary model:** `qwen2.5-coder:7b`
- **Desktop UI:** Python with Tkinter

Your hardware and installed software may differ if you reuse this project elsewhere.

## Architecture

The setup intentionally separates the Git repository from the local runtime environment.

```text
/mnt/Experiment/
├── local-ai-lab/                 # Git repository and source code
│   ├── app/
│   │   └── launcher.py           # Desktop GUI
│   ├── scripts/
│   │   ├── chat.sh               # Chat helper
│   │   └── check-environment.sh  # Environment diagnostics
│   ├── config.example
│   ├── .gitignore
│   └── README.md
│
└── AI-Lab/                       # Local runtime environment
    ├── bin/
    │   └── ai-lab                # Launcher entry point
    ├── runtime/
    │   └── bin/ollama
    ├── models/                   # Downloaded model data
    └── config/
        └── ollama-home/          # Local Ollama configuration/data
```

This is a logical overview of the intended layout; optional files and exact paths can vary by installation.

### Why keep two directories?

- `local-ai-lab/` contains version-controlled application code and documentation.
- `AI-Lab/` contains the runtime, model weights, and local state.
- Large runtime/model files should not be committed to Git.
- The launcher should call the intended runtime explicitly rather than depending on an unrelated system-wide Ollama installation.

## Getting started

### 1. Prerequisites

The current setup expects:

- Ubuntu or a compatible Linux desktop.
- Python 3 and Tkinter.
- A working Ollama runtime and at least one downloaded model.
- A writable runtime/model location.
- A graphical desktop session to display the Tkinter interface.

For Ubuntu, Tkinter can usually be installed with:

```bash
sudo apt install python3-tk
```

Use the runtime and model paths configured for your own installation. The `/mnt/Experiment/AI-Lab` paths below are specific to the development machine.

### 2. Launch the desktop application

The intended user-facing command is:

```bash
ai-lab
```

The shell command/alias should resolve to the launcher entry point:

```text
/mnt/Experiment/AI-Lab/bin/ai-lab
```

The GUI source lives in the repository:

```text
/mnt/Experiment/local-ai-lab/app/launcher.py
```

If the command is not found, inspect its resolution:

```bash
type -a ai-lab
whence -va ai-lab
```

The `whence` command is available in Zsh. In Bash, use `type -a ai-lab`.

### 3. Check the environment

From the repository:

```bash
cd /mnt/Experiment/local-ai-lab
bash scripts/check-environment.sh
```

Run the script with Bash unless its interpreter and syntax have explicitly been made compatible with another shell.

### 4. Verify the Ollama runtime and model

Check the installed models using the dedicated runtime:

```bash
/mnt/Experiment/AI-Lab/runtime/bin/ollama list
```

This command requires the relevant Ollama server to be running. If it reports a connection error, check the configured server lifecycle and launch workflow before assuming the model is missing.

The primary configured model is:

```text
qwen2.5-coder:7b
```

## Runtime and data management

Local AI Lab is intended to use the dedicated runtime under `/mnt/Experiment/AI-Lab`, rather than requiring a permanently running system-wide Ollama service.

The intended configuration separates:

- **Runtime executable:** `/mnt/Experiment/AI-Lab/runtime/bin/ollama`
- **Model storage:** `/mnt/Experiment/AI-Lab/models`
- **Local Ollama state:** `/mnt/Experiment/AI-Lab/config/ollama-home`
- **Local API endpoint:** `127.0.0.1:11434`

The exact environment variables and server lifecycle should be verified against the current launcher and configuration files. In particular, confirm that the server starts when needed and stops when the application exits before relying on that behavior.

## Development

Clone the source repository:

```bash
git clone https://github.com/MahmudNiloy680/local-ai-lab.git
cd local-ai-lab
```

Review the example configuration and scripts before running them on another machine. The current paths may need to be adjusted for a different installation.

### Useful checks

```bash
git status --short
git diff --check
bash scripts/check-environment.sh
```

Keep downloaded model weights, runtime binaries, machine-specific configuration, and generated logs out of the source repository. Check `.gitignore` before staging new files.

## Project checklist

### Implemented or established

- [x] Dedicated directory for the Ollama runtime and model storage.
- [x] Qwen 2.5 Coder 7B configured as the primary model.
- [x] Git repository and GitHub remote established.
- [x] `.gitignore` and example configuration.
- [x] Environment diagnostic script.
- [x] Chat helper script.
- [x] Python/Tkinter desktop launcher source.
- [x] `ai-lab` entry-point approach linking the desktop workflow to the local runtime.

### In progress / needs verification

- [ ] Validate the complete `ai-lab` workflow from a fresh terminal.
- [ ] Verify model discovery and chat from the GUI.
- [ ] Confirm reliable server start/stop behavior.
- [ ] Test error messages for missing binaries, unavailable server, and missing models.
- [ ] Confirm GPU acceleration during actual inference.
- [ ] Improve GUI status, progress feedback, and error reporting.
- [ ] Add lightweight tests for launch-path resolution and helper scripts.
- [ ] Finish installation, troubleshooting, and recovery documentation.

See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for the more detailed progress checklist and prioritized roadmap.

## Roadmap

1. **Reliability:** validate the launch, model selection, inference, and shutdown workflow.
2. **Desktop experience:** improve server status, model refresh, progress reporting, and error handling.
3. **Setup and portability:** reduce hard-coded paths where practical and document dependencies.
4. **Quality:** add tests and reproducible verification steps.
5. **Project presentation:** add screenshots and a short demonstration once the interface is stable.

## Contributing

Contributions and practical bug reports are welcome. Before submitting changes:

1. Test the affected workflow locally.
2. Run `git diff --check`.
3. Ensure no model weights, runtime binaries, credentials, or machine-specific secrets are included.
4. Document any new configuration options or dependencies.

## License

See the repository's [`LICENSE`](LICENSE) file.
