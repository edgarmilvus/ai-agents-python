#!/usr/bin/env bash
# Chapter 13 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_13.log"
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
echo "=== chapter 13: Human-in-the-Loop - Approval Steps and Interruption Patterns" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_approval_gate.py"
run_harness "advanced_application_script/example" "run_state_machine.py"
run_harness "comprehensive_solution_structure/example" "run_solution_structure.py"
run_harness "shared_boilerplate_for_the_solutions/example" "run_shared_boilerplate.py"
run_harness "exercise_1_the_atomic_action_approval_gate/exercise" "run_atomic_approval.py"
run_harness "exercise_2_dynamic_interruption_and_redirecti/exercise" "run_interruption.py"
run_harness "exercise_3_contextual_state_reporting_and_ris/exercise" "run_risk_reporting.py"
run_harness "exercise_4_interactive_challenge_multi_tier_s/exercise" "run_secure_deployment.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 13: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 13: ok" | tee -a "$LOG"
exit 0
