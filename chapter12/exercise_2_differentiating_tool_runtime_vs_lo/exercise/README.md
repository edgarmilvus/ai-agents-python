# Exercise 2 — runtime versus logical failures

## What it does

One tool, two failure modes: a network timeout is a runtime failure with a retry plan, a 404 is a logical failure with a replan.

## The listings

| file | what it is |
| --- | --- |
| `01_error_classification.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the outcome |

## Run it

```bash
cd chapter12/exercise_2_differentiating_tool_runtime_vs_lo/exercise/files
python3 01_error_classification.py
```

The listing is the run: it classifies a network failure and a 404 and prints the recovery plan for each. `run_exercise.py` asserts both plans and exits non-zero if a classification loses its strategy.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The mock's trigger is now `recovery strategy`, the wording the prompt actually uses.
