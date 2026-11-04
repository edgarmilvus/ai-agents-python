#!/usr/bin/env bash
# Run the model-calling listings against the real API. Not a CI check: this one
# costs money, and it needs OPENAI_COMPATIBLE_API_KEY exported.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" "$ROOT/tools/live_runner.py" "$@"
