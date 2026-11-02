#!/usr/bin/env bash
# Start local Laya (Jev-compatible /v1/systemone on http://127.0.0.1:8000)
# Usage: ./scripts/start_laya.sh
# Optional: ./scripts/start_laya.sh cpu | cuda | auto

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEVICE="${1:-auto}"
VENV_PY="$ROOT/.venv-laya/bin/python"
VENV_SERVE="$ROOT/.venv-laya/bin/laya-serve"

resolve_device() {
  case "$DEVICE" in
    cpu) echo cpu ;;
    cuda) echo cuda ;;
    auto)
      if "$VENV_PY" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        echo cuda
      elif "$VENV_PY" -c "import torch; raise SystemExit(0 if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available() else 1)" 2>/dev/null; then
        echo mps
      else
        echo cpu
      fi
      ;;
    *)
      echo "Usage: $0 [auto|cpu|cuda]" >&2
      exit 2
      ;;
  esac
}

if [[ ! -x "$VENV_PY" ]]; then
  echo "Creating .venv-laya and installing Laya (first run may take several minutes)..."
  python3 -m venv .venv-laya
  "$VENV_PY" -m pip install -U pip

  if [[ "$DEVICE" == "cpu" ]]; then
    "$VENV_PY" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
  else
    # Prefer CUDA wheels on Linux; fall back to default/CPU if unavailable.
    if ! "$VENV_PY" -m pip install torch --index-url https://download.pytorch.org/whl/cu124; then
      "$VENV_PY" -m pip install torch
    fi
    if ! "$VENV_PY" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)"; then
      echo "CUDA not available in torch — installing CPU build."
      "$VENV_PY" -m pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cpu
    fi
  fi

  "$VENV_PY" -m pip install "laya[serve]"
fi

RESOLVED="$(resolve_device)"

export LAYA_HOST=127.0.0.1
export LAYA_PORT=8000
export LAYA_DEVICE="$RESOLVED"
export LAYA_MODELS=english,multilingual
export LAYA_PRELOAD=1
export LAYA_DEFAULT_MODEL=english
export LAYA_MAX_LOADED=2
export NO_PROXY=localhost,127.0.0.1

echo "Starting laya-serve on http://127.0.0.1:8000 (device=$RESOLVED, models=english+multilingual)"
echo "Ctrl+C to stop. UI: .venv-laya/bin/python scripts/lab_ui.py"
exec "$VENV_SERVE"
