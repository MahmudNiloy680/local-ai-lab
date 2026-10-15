#!/usr/bin/env bash
set -u

BASE="/mnt/All/LLM-Exp"
HOST="127.0.0.1:11434"

section() {
    printf '\n%s\n' "$1"
    printf '%s\n' "--------------------------------"
}

echo "Local AI Lab — Environment Check"
echo "================================"

section "Operating System"
if [[ -r /etc/os-release ]]; then
    . /etc/os-release
    echo "${PRETTY_NAME:-Linux}"
else
    echo "Unable to identify operating system"
fi

section "Basic Tools"
for tool in bash git curl mountpoint; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf '%-12s %s\n' "$tool" "$(command -v "$tool")"
    else
        printf '%-12s %s\n' "$tool" "NOT FOUND"
    fi
done

section "AI Lab Storage Partition"
if mountpoint -q /mnt/All; then
    echo "Mounted: yes"
    df -h /mnt/All
else
    echo "Mounted: no"
    echo "The /mnt/All storage partition is unavailable."
fi

section "Ollama Runtime"
binary="$BASE/runtime/bin/ollama"

if [[ -x "$binary" ]]; then
    echo "Found: $binary"
    "$binary" --version 2>&1 | head -n 2
else
    echo "Not executable: $binary"
fi

if command -v ollama >/dev/null 2>&1; then
    echo "PATH command: $(command -v ollama)"
    ollama --version 2>&1 | head -n 2
else
    echo "Ollama is not available in PATH."
fi

section "Model Storage"
if [[ -d "$BASE/models" ]]; then
    du -sh "$BASE/models" 2>/dev/null || true
else
    echo "Model directory not found: $BASE/models"
fi

section "NVIDIA GPU"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name --format=csv,noheader 2>&1 ||
        echo "GPU query failed"
else
    echo "nvidia-smi unavailable"
fi

section "Local Ollama API"
if command -v curl >/dev/null 2>&1 &&
    curl -fsS --max-time 2 "http://$HOST/api/version"; then
    echo
else
    echo "No responding local server at $HOST"
fi

echo
echo "Diagnostic complete. No system changes made."
