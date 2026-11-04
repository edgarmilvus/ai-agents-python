#!/usr/bin/env bash
# Chapter 4 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_4.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import pydantic, langchain_classic, langchain_openai" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 4 (pydantic, langchain-classic, langchain-openai)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 4: Reasoning Loops - Chain of Thought (CoT) and ReAct" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_cot_chain.py"
run_harness "advanced_application_script/example" "run_react_agent.py"
run_harness "exercise_1_enforcing_structured_cot_for_audit/exercise" "run_structured_cot.py"
run_harness "exercise_2_implementing_a_minimalist_iterativ/exercise" "run_react_loop.py"
run_harness "exercise_3_interactive_challenge_dynamic_reac/exercise" "run_dynamic_react.py"
run_harness "exercise_4_structured_react_output_via_pydant/exercise" "run_schema_agent.py"
run_harness "exercise_5_comparative_analysis_cot_vs_react/exercise" "run_cot_vs_react.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 4: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 4: ok" | tee -a "$LOG"
exit 0
