#!/usr/bin/env bash
# Chapter 7 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_7.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import crewai" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 7 (crewai)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 7: Using CrewAI - Role-Playing Agents and Task Delegation" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_basic_crew.py"
run_harness "advanced_application_script/example" "run_marketing_crew.py"
run_harness "exercise_setup/example" "run_exercise_setup.py"
run_harness "solution_template_and_code_structure/example" "run_solution_template.py"
run_harness "exercise_1_the_technical_content_writer_crew/exercise" "run_crew.py"
run_harness "exercise_2_the_financial_analysis_crew_delega/exercise" "run_crew.py"
run_harness "exercise_3_the_global_product_launch_crew_hie/exercise" "run_crew.py"
run_harness "exercise_4_interactive_challenge_integrating/exercise" "run_crew.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 7: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 7: ok" | tee -a "$LOG"
exit 0
