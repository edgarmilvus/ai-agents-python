#!/usr/bin/env bash
# Chapter 19 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_19.log"
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
echo "=== chapter 19: The Economics of Agents - Token Cost Management and Optimization" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_cost_tracker.py"
run_harness "advanced_application_script/example" "run_optimized_pipeline.py"
run_harness "worked_example_solution_shells_for_reference/example" "run_solution_shells.py"
run_harness "exercise_1_asynchronous_token_budget_manager/exercise" "run_exercise.py"
run_harness "exercise_2_context_window_trimming_via_re_ran/exercise" "run_exercise.py"
run_harness "exercise_3_persistent_caching_for_agent_tools/exercise" "run_exercise.py"
run_harness "exercise_4_interactive_challenge_enforcing_st/exercise" "run_exercise.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 19: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 19: ok" | tee -a "$LOG"
exit 0
