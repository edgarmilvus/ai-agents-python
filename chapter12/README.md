# Chapter 12 — Self-Correction: Implementing Reflection and Error Recovery

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_self_correcting_architecture.py` | generate, validate, re-plan |
| `advanced_application_script/example/` | `01_reflection_loop.py` | a failed tool call corrected by reflection |
| `python_code_framework_for_exercises/example/` | `01_exercise_framework.py` | the shared infrastructure of the five exercises |
| `exercise_1_the_format_validator_reflection_lo/exercise/` | `01_format_validator.py` | raw output versus instruction |
| `exercise_2_differentiating_tool_runtime_vs_lo/exercise/` | `01_error_classification.py` | runtime versus logical failure |
| `exercise_3_recursive_error_recovery_with_dyna/exercise/` | `01_recursive_recovery.py` | feedback becoming the next prompt |
| `exercise_4_interactive_challenge_robust_confi/exercise/` | `02_robust_config.py` | `sys.argv` checked before the agent starts |
| `exercise_5_implementing_a_tool_failure_handle/exercise/` | `01_error_registry.py` | exception types mapped to handlers |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter12/run_offline.sh
```

`run_offline.sh` runs the eight harnesses and prints one line per harness; the log is
written to `chapter12/output/run_12.log`. Any harness that fails makes the suite
exit 1. Everything here is standard library and runs offline.

## What the harnesses caught

Every failure in this chapter was the same shape: a mock keyed on a phrase the
prompt no longer contained, or scanning the whole prompt when only part of it
counted.

- **The validator accepted everything.** The mock looked for `validate json`, but
  the prompt says "strict JSON schema validator"; once triggered, it scanned the
  whole prompt — which contains the schema, and therefore every required key.
  It now matches the prompt and reads only the `RAW OUTPUT:` section.
- **The reviewer rejected every rewrite.** Its prompt carries the constraint,
  which names the forbidden list comprehension, so the check fired on the
  instruction rather than the code. It now looks only at the code section.
- **Two recovery strategies were empty.** The mock waited for
  `generate recovery strategy`; the prompt says "generate a recovery strategy".
- **The reflection loop aborted.** It keyed on `Missing Ticker`, while the tool
  raises `Ticker cannot be empty`.
