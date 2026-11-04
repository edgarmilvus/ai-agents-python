# Exercise 5 — the failure handler registry

## What it does

A registry maps exception types to handlers: a network failure and a database failure each produce their own recovery action, and a healthy tool still runs.

## The listings

| file | what it is |
| --- | --- |
| `01_error_registry.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the outcome |

## Run it

```bash
cd chapter12/exercise_5_implementing_a_tool_failure_handle/exercise/files
python3 01_error_registry.py
```

The listing is the run: it routes a network failure and a database failure to their handlers. `run_exercise.py` asserts both and exits non-zero if a healthy tool stops running.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The registry is a dictionary keyed by exception class, so a new failure mode is an entry, not a branch.
