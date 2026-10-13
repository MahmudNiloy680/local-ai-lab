# Local AI Lab

A local-first AI workspace for running and managing language models on Ubuntu. Local AI Lab combines a Python/Tkinter desktop launcher with a dedicated Ollama runtime and model storage, keeping application source code separate from runtime binaries and large model files.

**Project status:** Active development. The desktop GUI, model controls, resource monitoring, and Ollama server lifecycle management are implemented. Failure-case testing, portability, and further reliability improvements remain in progress.

See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for the detailed implementation checklist, verified milestones, and development roadmap.

## Overview

Local AI Lab is designed around five principles:

- **Local-first:** Run language models on your own machine.
- **Separation of concerns:** Keep source code, runtime binaries, model weights, and local configuration separate.
- **Simple workflow:** Launch the desktop application using `ai-lab`.
- **GPU-aware:** Monitor available GPU resources and use GPU acceleration when supported by the hardware, driver, model, and Ollama runtime.
- **Maintainability:** Keep large model files and runtime binaries out of Git.

## Features

- Python/Tkinter desktop launcher.
- Model selection and model-list refresh.
- Ollama server start and stop controls.
- Detection of an existing Local AI Lab Ollama server.
- Process identity verification before terminating the server.
- Confirmation dialog when closing the GUI with an active server.
- GPU telemetry and RAM tracking.
- Scrollable GUI content.
- Model-aware terminal titles for chat sessions.
- Environment diagnostic script.
- Separate runtime and model storage.

Some failure scenarios and portability improvements still require testing. Refer to the project status document for the current checklist.

## Current environment

The original development environment is:

| Component | Configuration |
|---|---|
| Operating system | Ubuntu 26.04.1 LTS |
| Laptop | Lenovo LOQ 15IRX9 |
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU, 6 GB VRAM |
| Runtime | Ollama |
| Primary model | `qwen2.5-coder:7b` |
| Desktop interface | Python with Tkinter |
| Local API | `127.0.0.1:11434` |

These are the development machine's specifications, not requirements for every installation.

## Architecture

The source repository and local runtime are deliberately separated.

```text
/mnt/Experiment/
├── local-ai-lab/                  # Git repository
│   ├── app/
│   │   └── launcher.py            # Desktop GUI
│   ├── bin/
│   │   └── chat-qwen              # Chat helper entry point
│   ├── scripts/
│   │   ├── chat.sh                # Chat helper
│   │   └── check-environment.sh   # Environment diagnostics
│   ├── config.example
│   ├── .gitignore
│   ├── LICENSE
│   ├── README.md
│   └── PROJECT_STATUS.md
│
└── AI-Lab/                        # Local runtime environment
    ├── bin/
    │   └── ai-lab                 # Desktop launcher entry point
    ├── runtime/
    │   └── bin/ollama             # Dedicated Ollama executable
    ├── models/                    # Downloaded model data
    └── config/
        └── ollama-home/           # Local Ollama configuration/state
```

This is a logical overview of the development setup. Exact paths and optional files may differ on other machines.

### Why separate the directories?

- `local-ai-lab/` contains version-controlled application source, scripts, and documentation.
- `AI-Lab/` contains the runtime, downloaded models, and local configuration.
- Large model weights and runtime binaries do not belong in the source repository.
- The application should use its intended Ollama runtime rather than accidentally depending on an unrelated system-wide installation.

## Getting started

### 1. Prerequisites

The current application expects:

- Ubuntu or a compatible Linux desktop.
- Python 3.
- Tkinter.
- A working Ollama runtime and at least one downloaded model.
- A writable location for runtime files, models, and configuration.
- A graphical desktop session for the Tkinter interface.

On Ubuntu, Tkinter can usually be installed with:

```bash
sudo apt install python3-tk
```

NVIDIA GPU acceleration additionally depends on compatible hardware, drivers, and runtime support. CPU execution may be possible depending on the model and available system resources.

### 2. Launch the application

On the development machine, the intended command is:

```bash
ai-lab
```

The entry point is located at:

```text
/mnt/Experiment/AI-Lab/bin/ai-lab
```

The desktop application source is:

```text
/mnt/Experiment/local-ai-lab/app/launcher.py
```

If the command is not found, inspect how your shell resolves it:

```bash
type -a ai-lab
whence -va ai-lab
```

`whence` is available in Zsh. In Bash, use `type -a ai-lab`.

The entry point and runtime paths above are specific to the development machine. They are not automatically configured by cloning the repository.

### 3. Check the environment

From the repository directory:

```bash
cd /mnt/Experiment/local-ai-lab
bash scripts/check-environment.sh
```

Review the script before running it on another machine and adjust any machine-specific configuration as needed.

### 4. Check the Ollama runtime and models

The dedicated runtime is located at:

```text
/mnt/Experiment/AI-Lab/runtime/bin/ollama
```

Check available models:

```bash
/mnt/Experiment/AI-Lab/runtime/bin/ollama list
```

This command requires the relevant Ollama server to be available.

The primary configured model is:

```text
qwen2.5-coder:7b
```

If the command reports a connection error, first check the server's state rather than assuming that the model has been deleted.

## Runtime and server management

Local AI Lab is designed to use the dedicated Ollama runtime and avoid requiring a permanently running system-wide Ollama service.

The current development configuration uses:

| Resource | Location |
|---|---|
| Runtime executable | `/mnt/Experiment/AI-Lab/runtime/bin/ollama` |
| Model storage | `/mnt/Experiment/AI-Lab/models` |
| Local Ollama configuration | `/mnt/Experiment/AI-Lab/config/ollama-home` |
| Local API endpoint | `127.0.0.1:11434` |

The desktop application includes server controls and process detection for its configured Ollama executable.

### Shutdown behavior

When the GUI is closed while a Local AI Lab server is running, the application asks whether to stop the server and close the GUI.

- **Yes:** Request termination of the verified Local AI Lab server, then close the GUI if shutdown is confirmed.
- **No:** Cancel the close operation and leave the GUI open.
- **Unverified server:** Avoid terminating a process that cannot be verified as belonging to this Local AI Lab runtime.

Stopping the server interrupts active model sessions. The GUI's process checks are intended to avoid broad process-killing commands that might affect unrelated Ollama instances.

Failure scenarios and unusual process states remain part of ongoing regression testing.

## Development

Clone the source repository:

```bash
git clone https://github.com/MahmudNiloy680/local-ai-lab.git
cd local-ai-lab
```

Cloning the repository provides the source code and documentation. It does not automatically install the separate runtime, download model weights, or configure the development machine's `ai-lab` entry point.

Review `config.example`, `.gitignore`, and the scripts before adapting the project to another environment.

### Useful checks

Check the working tree:

```bash
git status --short
```

Check for whitespace errors:

```bash
git diff --check
```

Validate the Python launcher syntax:

```bash
python3 -m py_compile app/launcher.py
```

Run the environment diagnostic script:

```bash
bash scripts/check-environment.sh
```

These checks help identify basic repository, syntax, and environment issues. They do not replace end-to-end testing of the GUI and model workflow.

## Project checklist

### Implemented

- [x] Dedicated Ollama runtime and model storage.
- [x] Qwen 2.5 Coder 7B configured as the primary model.
- [x] Git repository, license, and `.gitignore`.
- [x] Environment diagnostic and chat helper scripts.
- [x] Python/Tkinter desktop launcher.
- [x] Model selection and refresh controls.
- [x] Server lifecycle controls and process detection.
- [x] Verified-process termination and close confirmation.
- [x] GPU telemetry and RAM tracking.
- [x] Scrollable GUI content and model-aware terminal titles.

### Remaining work

- [ ] Test missing-runtime, missing-model, unavailable-server, and occupied-port scenarios.
- [ ] Check for stale processes after GUI shutdown.
- [ ] Improve error messages and logging.
- [ ] Prevent long-running operations from freezing the GUI.
- [ ] Review process handling for race conditions and unexpected termination.
- [ ] Improve configuration and portability.
- [ ] Add lightweight regression tests.
- [ ] Complete setup and troubleshooting documentation.
- [ ] Add screenshots or a short demonstration when the interface is stable.

For detailed progress and prioritized tasks, see [`PROJECT_STATUS.md`](PROJECT_STATUS.md).

## Roadmap

1. **Reliability:** Test startup, model selection, chat, shutdown, and failure recovery.
2. **Desktop experience:** Improve responsiveness, status reporting, and error handling.
3. **Portability:** Reduce hard-coded paths and document setup requirements.
4. **Quality:** Add reproducible regression tests and verification steps.
5. **Presentation:** Add screenshots and a demonstration of the working application.

## Contributing

Practical bug reports and contributions are welcome.

Before submitting changes:

1. Test the affected workflow locally.
2. Run `git diff --check`.
3. Validate Python syntax when changing Python files.
4. Keep model weights, runtime binaries, credentials, and machine-specific secrets out of Git.
5. Document new configuration options and dependencies.

## License

See the [`LICENSE`](LICENSE) file.
