#!/usr/bin/env bash
# glmfix — run from source on macOS
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$SCRIPT_DIR/glmfix.py" "$@"
