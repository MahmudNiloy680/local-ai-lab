# Local AI Lab — Project Status

> **Status snapshot:** 13 October 2026  
> **Current milestone:** Desktop GUI and Ollama lifecycle management  
> **Latest commit:** `b055ab8` — Improve Ollama server lifecycle management

## Overview

Local AI Lab is a local-first AI workspace for running and managing language models on Ubuntu. The project aims to make local LLM experimentation convenient while preserving the existing Ollama runtime, model storage, and configuration.

The primary workflow is:

```bash
ai-lab
```

The project is organized into two separate directories:

- **`local-ai-lab/`** — Git repository containing the application, scripts, and documentation.
- **`AI-Lab/`** — Runtime environment, model storage, configuration, and application entry point.

The current environment uses Ollama, Qwen 2.5 Coder 7B, and an NVIDIA RTX 3050 Laptop GPU.

## Architecture

```text
/mnt/All/LLM-Exp/
├── local-ai-lab/                  # Git repository
│   ├── app/
│   │   └── launcher.py            # Tkinter desktop GUI
│   ├── scripts/
│   │   ├── chat.sh                # Chat helper
│   │   └── check-environment.sh   # Environment diagnostics
│   ├── README.md
│   ├── LICENSE
│   └── .gitignore
│
└── AI-Lab/                        # Local runtime environment
    ├── bin/
    │   └── ai-lab                 # GUI entry point
    ├── runtime/
    │   └── bin/ollama             # Ollama executable
    ├── models/                    # Model weights
    └── config/
        └── ollama-home/           # Ollama configuration/home
```

This is a logical overview, not an exhaustive file inventory. Verify exact paths on the machine when changing the architecture.

## Current implementation status

### 1. Foundation and environment

- [x] Establish the dedicated Ollama runtime.
- [x] Keep model storage outside the Git source repository.
- [x] Configure Qwen 2.5 Coder 7B for local use.
- [x] Create the `local-ai-lab` Git repository and publish it to GitHub.
- [x] Add a project license and `.gitignore`.
- [x] Create `scripts/check-environment.sh`.
- [x] Establish the separate `AI-Lab/bin/ai-lab` entry point.
- [x] Resolve the previously reported missing-entry-point path issue.

### 2. Desktop GUI

- [x] Build the Python/Tkinter desktop launcher in `app/launcher.py`.
- [x] Add model selection and model-list refresh.
- [x] Add Ollama server start/stop controls.
- [x] Add GPU telemetry and RAM tracking.
- [x] Improve the interface with a scrollable content area.
- [x] Improve chat terminal titles based on the selected model.
- [x] Add a confirmation dialog when closing the GUI with an active Local AI Lab server.
- [x] Add process detection for the existing Local AI Lab Ollama executable.
- [x] Implement verified-process termination so a reopened GUI can manage a surviving server.
- [x] Preserve the option to cancel closing and keep the GUI open.

### 3. Server lifecycle management

- [x] Detect whether the Ollama API is responding.
- [x] Identify the running server by its executable path and command.
- [x] Support managing a server that remains running after the GUI has been reopened.
- [x] Require confirmation before stopping a server through the GUI.
- [x] Verify the target process before sending termination signals.
- [x] Avoid broad process-killing commands such as `pkill ollama`.
- [x] Add a timeout and forced-stop fallback to the shutdown helper.
- [x] Commit the lifecycle-management changes as `b055ab8`.

**Expected close-dialog behavior**

- **Yes:** stop the verified Local AI Lab Ollama server and close the GUI.
- **No:** cancel the close operation and keep the GUI open.

If a responding server cannot be verified against the configured runtime, the GUI should avoid stopping it automatically.

### 4. Chat and model workflow

- [x] Configure the local runtime and model directory.
- [x] Establish the GUI-based model-launching workflow.
- [x] Verify a complete chat session from a fresh GUI launch.
- [x] Verify that the selected model produces a response successfully.
- [ ] Test behavior when the configured model is missing.
- [ ] Test behavior when the server fails to start or the port is occupied.

### 5. Git and repository maintenance

- [x] Track application source separately from runtime binaries and model weights.
- [x] Commit the latest server lifecycle changes.
- [x] Run Python syntax validation and `git diff --check` during development.
- [x] Review and document the latest commit and feature changes in `README.md`.
- [x] Record preliminary local model benchmark results in `BENCHMARKS.md`.
- [ ] Review the remaining untracked backup files before deciding whether to retain or remove them.
- [ ] Push the latest commit to GitHub if it has not already been pushed.

## Next milestones

### P0 — Reliability and regression testing

- [x] Test the complete workflow from a fresh terminal using `ai-lab`.
- [x] Confirm model discovery and refresh.
- [x] Test server startup, shutdown, and reopening the GUI while Ollama remains active.
- [x] Test the close dialog with both **Yes** and **No**.
- [x] Confirm GPU telemetry and RAM tracking continue updating.
- [x] Confirm terminal chat launches with the selected model and returns a response.
- [ ] Test failure cases: missing runtime, unavailable API, missing model, and occupied port.
- [ ] Check for stale server processes after GUI shutdown.

### P1 — Desktop experience

- [x] Improve status messages for stopped, starting, running, and failed states.
- [ ] Make errors actionable and provide useful log locations.
- [ ] Prevent long-running operations from freezing the GUI.
- [ ] Improve model metadata and resource-usage visibility.
- [ ] Review process handling for race conditions and unexpected termination.

### P2 — Setup and portability

- [ ] Add a setup and verification guide for system dependencies.
- [ ] Review hard-coded paths and document the current storage layout.
- [ ] Add configurable runtime and model-directory paths without moving existing data.
- [ ] Document recovery steps for failed launches and interrupted server sessions.
- [ ] Test after logout, reboot, and launch from a fresh terminal.
- [x] Confirmed active scripts use the migrated runtime location.

### P3 — Documentation and quality

- [ ] Update `README.md` with the current architecture, features, and usage instructions.
- [ ] Add a manual regression-test checklist or lightweight automated tests.
- [ ] Verify that runtime binaries, model weights, logs, and local configuration are excluded from Git.
- [ ] Add screenshots or a short demo after the interface stabilizes.
- [ ] Keep this project status synchronized with future commits.

## Immediate execution plan

1. Launch the GUI using `ai-lab`.
2. Confirm the installed model appears in the model list.
3. Start Ollama and verify that a chat session works.
4. Test server stopping and GUI closing, including both close-dialog choices.
5. Verify GPU telemetry, RAM tracking, and model refresh.
6. Check the repository:

   ```bash
   cd /mnt/All/LLM-Exp/local-ai-lab
   git status --short
   git log -3 --oneline
   git diff --check
   ```

7. Update the README, commit the documentation separately, and push the changes when ready.

## Scope and safety constraints

- Preserve the existing Ollama runtime, model storage, scripts, and Git repository.
- Do not download duplicate models or relocate model data during routine GUI development.
- Do not mark untested functionality as complete.
- Verify process identity before stopping a server.
- Keep runtime binaries and large model weights outside the source repository.
- Make changes incrementally and validate each change before proceeding.
