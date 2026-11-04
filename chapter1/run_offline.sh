#!/usr/bin/env bash
# Chapter 1 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_1.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import pydantic, langchain_core" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 1 (pydantic, langchain-core)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 1: Beyond the Prompt - What Are Autonomous Agents?" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_agentic_loop.py"
run_harness "advanced_application_script/example" "run_validation_agent.py"
run_harness "exercise_1_simulating_the_ooda_loop/exercise" "run_ooda_collector.py"
run_harness "exercise_2_implementing_rudimentary_episodic/exercise" "run_episodic_memory.py"
run_harness "exercise_3_rule_based_tool_routing_and_execut/exercise" "run_tool_router.py"
run_harness "exercise_4_interactive_challenge_introducing/exercise" "run_planning_layer.py"
run_harness "worked_example_the_whole_chapter_in_one_scrip/example" "run_worked_example.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 1: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 1: ok" | tee -a "$LOG"
exit 0
