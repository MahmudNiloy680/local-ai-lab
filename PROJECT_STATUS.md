# Local AI Lab — Project Status

> **Status snapshot:** 12 October 2026  
> **Purpose:** Track the current implementation, verified progress, and next milestones for the Local AI Lab project.

## Overview

Local AI Lab is a local-first AI workspace for running and managing language models on Ubuntu. The objective is to keep the existing Ollama runtime and model storage intact while providing a convenient desktop launcher and a simple command-line entry point.

The primary user workflow is intended to be:

```bash
ai-lab
```

The project is split across two directories with separate responsibilities:

- **`local-ai-lab/`** — Git repository containing application source code, scripts, and documentation.
- **`AI-Lab/`** — Existing runtime environment, model storage, and launch entry point.

The current setup includes Ollama, the Qwen 2.5 Coder 7B model, and an NVIDIA RTX 3050 Laptop GPU.

## Architecture

```text
/mnt/Experiment/
├── local-ai-lab/                 # Git repository / source
│   ├── app/
│   │   └── launcher.py           # Desktop GUI
│   ├── scripts/
│   │   └── chat.sh               # Chat helper script
│   ├── scripts/check-environment.sh
│   ├── PROJECT_STATUS.md
│   ├── README.md
│   ├── LICENSE
│   └── .gitignore
│
└── AI-Lab/                       # Runtime environment
    ├── bin/
    │   └── ai-lab                # Single-command entry point
    ├── runtime/
    │   └── bin/ollama
    └── models/                   # Model storage
```

*The tree is a logical overview; confirm exact filenames and paths with `find` before treating it as an exhaustive inventory.*

## Progress checklist

### Foundation and environment

- [x] Set up the existing Ollama runtime under the dedicated `AI-Lab` directory.
- [x] Keep model storage separate from the Git source repository.
- [x] Configure Qwen 2.5 Coder 7B for local use.
- [x] Establish the `local-ai-lab` Git repository and publish the repository to GitHub.
- [x] Add a project license and `.gitignore`.
- [x] Create an environment diagnostic script at `scripts/check-environment.sh`.
- [x] Establish the `AI-Lab/bin/ai-lab` entry-point approach while keeping the GUI source in `local-ai-lab/app/launcher.py`.

### Application and launch workflow

- [x] Create `app/launcher.py` as the Python/Tkinter desktop application; the implementation was reported at approximately 540 lines.
- [x] Update `scripts/chat.sh`.
- [x] Configure the `ai-lab` shell alias to point to `/mnt/Experiment/AI-Lab/bin/ai-lab`.
- [x] Resolve the previously reported missing-entry-point path issue; the user subsequently confirmed completion.
- [x] Verify the complete workflow from a fresh terminal: run `ai-lab` and confirm that the GUI opens.
- [x] Verify model discovery, Ollama server start/stop, and terminal chat from the GUI.
- [x] Confirm that the configured model responds successfully after launching through the GUI.
- [ ] Test error handling when Ollama is unavailable or the configured model is missing.

> Checked items above reflect work reported as completed during development. Items that depend on a fresh end-to-end run remain unchecked until explicitly verified.

## Next steps — prioritized checklist

### P0 — End-to-end reliability

- [x] Run `ai-lab` from a fresh terminal and confirm that the GUI starts reliably.
- [x] Confirm the GUI and scripts consistently use the intended runtime at `/mnt/Experiment/AI-Lab/runtime/bin/ollama`.
- [x] Test server start, server stop, model listing/refresh, and chat.
- [x] Run `git diff --check` and review `git status` before committing.
- [ ] Capture and surface actionable errors for missing binaries, unavailable server, missing model, and failed commands.


### P1 — Improve the desktop experience

- [x] Show the active server state clearly (stopped, starting, running, or error).
- [x] Show available models and refresh the list on demand.
- [x] Display the selected model and useful model metadata where available.
- [x] Add a one-click action for the primary Qwen Coder chat workflow.
- [ ] Keep long-running operations from freezing the GUI; provide progress or status feedback.
- [ ] Ensure subprocesses are terminated cleanly and logs/errors are available for troubleshooting.

### P2 — Setup and portability

- [ ] Add a setup/verification script for required system dependencies and executable permissions.
- [ ] Validate paths relative to configuration where possible; document any intentionally fixed paths.
- [ ] Add a configuration option for runtime and model directories without moving existing data.
- [ ] Document a recovery procedure for a failed launch or stopped Ollama server.
- [ ] Test behavior after logout/reboot and from a shell that does not inherit the current terminal session.

### P3 — Quality and project presentation

- [x] Document prerequisites, installation, launch, troubleshooting, and supported workflows in `README.md`.
- [ ] Add a manual test checklist or lightweight automated tests for helper scripts and launch-path resolution.
- [ ] Review `.gitignore` to ensure model files, runtime binaries, logs, and local configuration are not accidentally committed.
- [ ] Add screenshots or a short demo of the GUI once the interface is stable.
- [ ] Keep this status checklist updated as milestones are completed.

## Suggested immediate execution plan

1. Open a fresh terminal and run `ai-lab`.
2. In the GUI, refresh the model list and confirm Qwen 2.5 Coder 7B is available.
3. Start Ollama, verify its running state, and test a short prompt.
4. Stop the server and verify that the GUI reports the stopped state correctly.
5. From the repository, run:

   ```bash
   git status --short
   git diff --check
   ```

6. Fix any issues found, then update the relevant checklist items and commit the verified changes.

## Scope and safety constraints

- Preserve the existing Ollama runtime, model storage, scripts, and Git repository.
- Do not download duplicate models or relocate model data as part of routine GUI improvements.
- Do not mark a feature complete until it has been tested.
- Keep the source repository separate from large runtime binaries and model weights.
