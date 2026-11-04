#!/usr/bin/env bash
# Chapter 2 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_2.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import langchain_classic, langchain_openai, langchain_core" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 2 (langchain-classic, langchain-openai)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 2: The Cognitive Architecture - Memory, Planning, and Tools" | tee -a "$LOG"
echo "    python: $("$PYTHON" -V 2>&1)" | tee -a "$LOG"

run_harness() {
  local project="$1"
  local harness="$2"
  local dir="$CHAPTER_DIR/$project"
  local log="$dir/output/harness.log"
  mkdir -p "$dir/output"
  if ( cd "$dir" && "$PYTHON" "files/$harness" ) > "$log" 2>&1; then
    # Some libraries print a banner on exit (CrewAI does), so the verdict is
    # found by its shape, not by being the last line.
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

run_harness "basic_code_example/example" "run_contextual_calculator.py"
run_harness "basic_code_example/example" "run_tool_description.py"
run_harness "advanced_application_script/example" "run_strategic_analyst.py"
run_harness "boilerplate_code_for_exercises/example" "run_boilerplate.py"
run_harness "exercise_1_contextual_reflection_and_knowledg/exercise" "run_contextual_reflection.py"
run_harness "exercise_2_hierarchical_planning_and_decompos/exercise" "run_hierarchical_planner.py"
run_harness "exercise_3_state_aware_tool_integration/exercise" "run_state_aware_tools.py"
run_harness "exercise_4_interactive_challenge_integrating/exercise" "run_constrained_planner.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 2: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 2: ok" | tee -a "$LOG"
exit 0
