#!/usr/bin/env bash
# Chapter 14 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_14.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import json" >/dev/null 2>&1; then
  echo "FAILED  python is not usable" | tee "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 14: Browser Agents - Automating the Web with Selenium and AI" | tee -a "$LOG"
echo "    python: $("$PYTHON" -V 2>&1)" | tee -a "$LOG"

run_harness() {
  local project="$1"
  local harness="$2"
  local dir="$CHAPTER_DIR/$project"
  local log="$dir/output/harness.log"
  mkdir -p "$dir/output"
  if ( cd "$dir" && "$PYTHON" "files/$harness" ) > "$log" 2>&1; then
    verdict=$(grep -E '^__VERDICT__ 0 ' "$log" | tail -n 1)
    if [ -n "$verdict" ]; then
      count=$(echo "$verdict" | awk '{print $3}')
      echo "ok      $project — $count assertions passed" | tee -a "$LOG"
    else
      echo "FAILED  $project (no verdict line)" | tee -a "$LOG"
      sed -n '1,20p' "$log" | sed 's/^/        /' | tee -a "$LOG"
      fail=1
    fi
  else
    echo "FAILED  $project" | tee -a "$LOG"
    sed -n '1,20p' "$log" | sed 's/^/        /' | tee -a "$LOG"
    fail=1
  fi
}

run_harness "basic_code_example/example" "run_browser_flow.py"
run_harness "advanced_application_script/example" "run_job_filter.py"
run_harness "python_implementation_structure/example" "run_browser_tool.py"
run_harness "exercise_1_the_dynamic_locator_decipherer/exercise" "run_exercise.py"
run_harness "exercise_2_autonomous_multi_page_task_flow_wi/exercise" "run_exercise.py"
run_harness "exercise_3_interactive_challenge_enhancing_re/exercise" "run_exercise.py"
run_harness "exercise_4_enforcing_dry_and_abstraction_with/exercise" "run_exercise.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 14: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 14: ok" | tee -a "$LOG"
exit 0
