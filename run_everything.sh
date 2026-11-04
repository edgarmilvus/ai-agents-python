#!/usr/bin/env bash
# Run every check the book ships, in the order that fails fastest:
#   1. the offline suite (133 harnesses, no key, no network)
#   2. the queue demo (chapter 18, needs Redis)
#   3. the browser run (chapter 14, needs Chrome and Selenium)
#   4. with --live, the live run (21 listings, costs about ten cents)
#
# Checks 2 and 3 are skipped with a message when the service or the package is
# missing, so this script is safe on a machine that has neither: it reports what
# it could not run instead of failing a chapter that is not broken.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

LIVE=0
for arg in "$@"; do
  case "$arg" in
    --live) LIVE=1 ;;
    -h|--help)
      awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      echo "unknown option: $arg (try --live or --help)" >&2
      exit 2
      ;;
  esac
done

fail=0
skipped=()

section() {
  printf '\n=== %s ===\n' "$1"
}

section "1/4 offline suite"
if "$ROOT/run_offline.sh"; then
  :
else
  fail=1
fi

section "2/4 queue demo (Redis)"
if command -v redis-server >/dev/null 2>&1; then
  if ! "$ROOT/run_queue_demo.sh"; then
    fail=1
  fi
else
  echo "skipped: redis-server not found"
  echo "  macOS: brew install redis"
  echo "  Debian/Ubuntu/WSL: sudo apt install redis-server"
  skipped+=("queue demo (no redis-server)")
fi

section "3/4 browser run (Chrome)"
chrome=0
for candidate in "google-chrome" "chromium" "chromium-browser"; do
  if command -v "$candidate" >/dev/null 2>&1; then chrome=1; fi
done
if [ -d "/Applications/Google Chrome.app" ]; then chrome=1; fi
if [ "$chrome" != 1 ]; then
  echo "skipped: Chrome not found"
  echo "  macOS: brew install --cask google-chrome"
  skipped+=("browser run (no Chrome)")
elif ! "$PYTHON" -c "import selenium, webdriver_manager" >/dev/null 2>&1; then
  # Selenium is an optional extra: the offline suite stubs it, so a copy that
  # installed only requirements.txt can run everything except this one listing.
  echo "skipped: selenium not installed for $PYTHON"
  echo "  \"$PYTHON\" -m pip install -r \"$ROOT/requirements-browser.txt\""
  skipped+=("browser run (no selenium)")
else
  LISTING="$ROOT/chapter14/basic_code_example/example/files/01_digital_librarian.py"
  if ! (cd "$(dirname "$LISTING")" && "$PYTHON" 01_digital_librarian.py); then
    fail=1
  fi
fi

if [ "$LIVE" = 1 ]; then
  section "4/4 live run"
  if [ -z "${OPENAI_COMPATIBLE_API_KEY:-}" ]; then
    echo "skipped: OPENAI_COMPATIBLE_API_KEY is not set"
    echo '  export OPENAI_COMPATIBLE_API_KEY="..."  # then rerun with --live'
    skipped+=("live run (no key)")
  elif ! "$ROOT/run_live.sh"; then
    fail=1
  fi
else
  section "4/4 live run"
  echo "skipped: pass --live to run it (21 listings, about ten cents)"
  skipped+=("live run (needs --live)")
fi

printf '\n---\n'
if [ "$fail" -ne 0 ]; then
  echo "everything: FAILED"
else
  echo "everything: ok"
fi
if [ "${#skipped[@]}" -gt 0 ]; then
  printf 'not run: %s\n' "$(IFS=', '; echo "${skipped[*]}")"
fi
exit "$fail"
