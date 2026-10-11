# Local AI Lab

A Linux-focused environment for running language models locally,
with GPU acceleration, configurable storage, and a command-line interface.

## Current Setup

- OS: Ubuntu Linux
- Runtime: Ollama
- Model: Qwen 2.5 Coder 7B
- GPU: NVIDIA RTX 3050 Laptop GPU
- Storage: Dedicated local partition
- Interface: Bash command-line launcher

## Goals

- Run language models locally
- Keep model weights and runtime binaries outside Git
- Support configurable runtime and model paths
- Simplify model startup and shutdown
- Provide environment diagnostics
- Document installation and troubleshooting

## Project Status

Early development. The existing working installation is maintained
separately from this repository.

## Planned Features

- [x] Initial project documentation
- [ ] Environment diagnostics
- [ ] Configurable chat launcher
- [ ] Setup automation
- [ ] Model management
- [ ] Installation and troubleshooting guides

## Safety

Never commit model weights, credentials, API keys, or machine-specific
configuration.

## License

See [LICENSE](LICENSE).
