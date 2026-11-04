#!/usr/bin/env bash
# Chapter 8 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_8.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import langgraph" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 8 (langgraph)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 8: Using LangGraph - Building Cyclic State Graphs for Agents" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_cyclic_graph.py"
run_harness "advanced_application_script/example" "run_research_graph.py"
run_harness "exercise_1_the_iterative_research_and_confide/exercise" "run_graph.py"
run_harness "exercise_2_defining_robust_state_with_pydanti/exercise" "run_graph.py"
run_harness "exercise_3_the_code_refinement_and_self_corre/exercise" "run_graph.py"
run_harness "exercise_4_interactive_challenge_enhancing_th/exercise" "run_graph.py"
run_harness "exercise_5_the_interactive_chatbot_with_tool/exercise" "run_graph.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 8: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 8: ok" | tee -a "$LOG"
exit 0
