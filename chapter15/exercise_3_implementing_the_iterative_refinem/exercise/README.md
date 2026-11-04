# Exercise 3 — the refinement orchestrator

## What it does

The loop a coding agent needs: generate a package, run its tests, and on failure build a feedback payload that names the attempt, the failing reason and the test output, then generate again.

## The listings

| file | what it is |
| --- | --- |
| `01_orchestrator.py` | the solution from the chapter |
| `run_exercise.py` | the harness: drives the solution and checks the outcome |

## Run it

```bash
cd chapter15/exercise_3_implementing_the_iterative_refinem/exercise/files
python3 run_exercise.py
```

`01_orchestrator.py` defines the loop with its usage commented out. The harness drives it through one failure and one success and exits non-zero if the loop stops feeding the failure back.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The scripted executor fails on odd attempts, so the demo is deterministic: attempt 1 fails, attempt 2 passes.
- The loop stops on the first success and returns the package; it never runs the remaining attempts.
- Standard library plus `pydantic`; offline. The sketch printed in the exercise text is book-only because it assumes the classes from the exercise above.
