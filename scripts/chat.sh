#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${AI_LAB_CONFIG:-$REPO_DIR/config/local-ai-lab.conf}"

if [[ ! -f "$CONFIG" ]]; then
    echo "ERROR: Configuration file not found: $CONFIG" >&2
    exit 1
fi

# Load local configuration.
source "$CONFIG"

BASE="${AI_LAB_BASE:?AI_LAB_BASE is not configured}"
MODEL="${1:-${AI_LAB_MODEL:-qwen2.5-coder:7b}}"
HOST="${AI_LAB_HOST:-127.0.0.1:11434}"
RUNTIME="${AI_LAB_RUNTIME:-runtime}"
OLLAMA="$BASE/$RUNTIME/bin/ollama"

if ! mountpoint -q /mnt/Experiment; then
    echo "ERROR: /mnt/Experiment is not mounted." >&2
    exit 1
fi

if [[ ! -x "$OLLAMA" ]]; then
    echo "ERROR: Ollama executable not found: $OLLAMA" >&2
    exit 1
fi

export HOME="$BASE/config/ollama-home"
export OLLAMA_MODELS="$BASE/models"
export OLLAMA_HOST="$HOST"

mkdir -p "$HOME" "$OLLAMA_MODELS"

if curl -fsS --max-time 2 "http://$HOST/api/version" >/dev/null 2>&1; then
    echo "ERROR: An Ollama server is already running at $HOST." >&2
    echo "Stop that server before launching this managed session." >&2
    exit 1
fi

"$OLLAMA" serve &
SERVER_PID=$!

cleanup() {
    trap - EXIT INT TERM
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

ready=false
for _ in {1..30}; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "ERROR: Ollama server exited unexpectedly." >&2
        exit 1
    fi

    if curl -fsS --max-time 2 "http://$HOST/api/version" >/dev/null 2>&1; then
        ready=true
        break
    fi

    sleep 1
done

if [[ "$ready" != true ]]; then
    echo "ERROR: Ollama server did not become ready." >&2
    exit 1
fi

echo "Starting model: $MODEL"
"$OLLAMA" run "$MODEL"
