#!/usr/bin/env bash
# Chapter 9 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_9.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import pydantic" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 9 (pydantic)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 9: Consensus and Critique - How Agents Review Each Other's Work" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_exercise.py"
run_harness "advanced_application_script/example" "run_exercise.py"
run_harness "unified_code_block_for_exercises_scaffold/example" "run_exercise.py"
run_harness "unified_code_block_for_exercises_complete/example" "run_exercise.py"
run_harness "exercise_1_enforcing_structured_feedback_with/exercise" "run_exercise.py"
run_harness "exercise_2_implementing_a_weighted_consensus/exercise" "run_exercise.py"
run_harness "exercise_3_designing_the_iterative_refinement/exercise" "run_exercise.py"
run_harness "exercise_4_interactive_challenge_semantic_rev/exercise" "run_exercise.py"
run_harness "exercise_5_auditability_and_persistence_of_cr/exercise" "run_exercise.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 9: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 9: ok" | tee -a "$LOG"
exit 0
