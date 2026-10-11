# Local AI Lab

A Linux-focused toolkit for running large language models locally with Ollama. Local AI Lab aims to make local inference easier to configure, launch, diagnose, and manage.

**Current environment:** Ubuntu · Ollama · Qwen 2.5 Coder 7B · NVIDIA RTX 3050 6GB

## Features

- Launch a local model through a Bash-based chat launcher
- Configure runtime paths, model selection, and API host
- Keep model weights and runtime binaries outside the Git repository
- Check system tools, GPU visibility, model storage, and API availability
- Run inference locally without sending prompts to a hosted AI API

## Project Structure

```text
local-ai-lab/
├── config.example
├── docs/
├── scripts/
│   ├── chat.sh
│   └── check-environment.sh
├── .gitignore
├── LICENSE
└── README.md
```

## Requirements

- Linux with Bash
- Git and curl
- Ollama runtime
- Sufficient RAM, disk space, and compute for your chosen model
- NVIDIA drivers and compatible GPU support for NVIDIA acceleration (optional)

## Configuration

Copy the example configuration into the ignored configuration directory:

```bash
mkdir -p config
cp config.example config/local-ai-lab.conf
nano config/local-ai-lab.conf
```

Set the paths and model appropriate for your system:

```bash
AI_LAB_BASE="$HOME/AI-Lab"
AI_LAB_MODEL="qwen2.5-coder:7b"
AI_LAB_HOST="127.0.0.1:11434"
AI_LAB_RUNTIME="runtime"
```

`AI_LAB_BASE` must point to a directory containing the configured runtime, model storage, and Ollama home directories. The example paths are templates; adapt them to your installation.

## Usage

### Check the environment

```bash
chmod +x scripts/check-environment.sh
./scripts/check-environment.sh
```

The diagnostic script checks system information, available tools, runtime paths, model storage, NVIDIA GPU visibility, and the local Ollama API. It does not start the server or download models.

### Start a chat session

```bash
chmod +x scripts/chat.sh
./scripts/chat.sh
```

The launcher starts the configured Ollama server, waits for its API, and launches the selected model. Type `/bye` to exit the interactive chat. The launcher then attempts to stop the server process it started.

Do not run another server on the same host and port while using this managed launcher.

## Storage and Git Hygiene

Keep large model files, runtime binaries, personal configuration, and secrets outside version control.

The repository ignores the local `config/` directory, so your machine-specific configuration should not be committed. `config.example` provides a safe starting template.

## Troubleshooting

- **Storage partition unavailable:** verify that your configured runtime directory is mounted and accessible.
- **Ollama executable not found:** check `AI_LAB_BASE`, `AI_LAB_RUNTIME`, and the executable path.
- **API connection refused:** confirm the launcher started successfully and the configured host and port are correct.
- **NVIDIA GPU not detected:** check your NVIDIA driver installation and `nvidia-smi`.
- **Model unavailable:** verify that the selected model is present in the configured Ollama model store.

## Roadmap

- [x] Initial project documentation
- [x] Environment diagnostic script
- [x] Configurable chat launcher
- [ ] Improve server lifecycle and process cleanup
- [ ] Model listing and selection
- [ ] Installation and setup automation
- [ ] Automated tests

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
