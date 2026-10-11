#!/usr/bin/env bash
set -u

echo "Local AI Lab — Environment Check"
echo "================================"

if [ -r /etc/os-release ]; then
    . /etc/os-release
    echo "OS: ${PRETTY_NAME:-Linux}"
fi

echo "Bash: $(bash --version | head -n 1)"
echo "Git: $(git --version 2>/dev/null || echo 'not installed')"

echo
echo "Ollama:"
if command -v ollama >/dev/null 2>&1; then
    command -v ollama
    ollama --version 2>&1 | head -n 2
else
    echo "Not found in PATH"
fi

echo
echo "NVIDIA GPU:"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name --format=csv,noheader \
        2>/dev/null || echo "GPU query failed"
else
    echo "nvidia-smi unavailable"
fi

echo
echo "Local Ollama API:"
if curl -fsS --max-time 2 http://127.0.0.1:11434/api/version\; then
    echo
else
    echo "No responding local server"
fi

echo
echo "Diagnostic complete. No system changes made."
