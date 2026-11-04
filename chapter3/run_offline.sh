#!/usr/bin/env bash
# Chapter 3 harness suite. Run from anywhere: every path is resolved from here.
set -uo pipefail

CHAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CHAPTER_DIR/.." && pwd)"
OUTPUT="$CHAPTER_DIR/output"
LOG="$OUTPUT/run_3.log"
mkdir -p "$OUTPUT"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [ -n "${PYTHON:-}" ]; then
  PYTHON="$PYTHON"
else
  PYTHON="python3"
fi

fail=0

if ! "$PYTHON" -c "import sqlalchemy, langchain_classic, langchain_openai" >/dev/null 2>&1; then
  echo "FAILED  dependencies missing for chapter 3 (sqlalchemy, langchain-classic, langchain-openai)" | tee "$LOG"
  echo "        $PYTHON -m pip install -r $ROOT/requirements.txt" | tee -a "$LOG"
  exit 1
fi

: > "$LOG"
echo "=== chapter 3: The Tool Belt - Connecting LLMs to APIs, Files, and the World" | tee -a "$LOG"
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

run_harness "basic_code_example/example" "run_tool_schema.py"
run_harness "advanced_application_script/example" "run_market_analyst.py"
run_harness "necessary_setup_code_block/example" "run_mock_services.py"
run_harness "starter_code_for_the_exercises/example" "run_exercise_tools.py"
run_harness "exercise_1_the_secure_configuration_manager_a/exercise" "run_secure_config.py"
run_harness "exercise_2_the_real_time_financial_analyst_ag/exercise" "run_financial_analyst.py"
run_harness "exercise_3_the_orm_inventory_query_agent_data/exercise" "run_orm_inventory.py"
run_harness "exercise_4_interactive_challenge_the_multi_mo/exercise" "run_deployment_analyst.py"
run_harness "exercise_5_tool_schema_validation_and_robustn/exercise" "run_schema_validation.py"

echo "---" | tee -a "$LOG"
if [ "$fail" -ne 0 ]; then
  echo "chapter 3: FAILED" | tee -a "$LOG"
  exit 1
fi
echo "chapter 3: ok" | tee -a "$LOG"
exit 0
