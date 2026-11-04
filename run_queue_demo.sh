#!/usr/bin/env bash
# Prove chapter 18's queue for real: Redis + rq worker + one finished job.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" "$ROOT/tools/queue_demo.py" "$@"
