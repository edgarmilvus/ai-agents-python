# Exercise 1 — the timeout-bound sandbox

## What it does

`execute_sandboxed_code` runs a snippet in a temporary file with a five-second limit and returns `success`, `stdout`, `stderr`, `exit_code` and `reason`. A timeout, an uncaught exception and an explicit `sys.exit(N)` are reported separately.

## The listings

| file | what it is |
| --- | --- |
| `01_sandbox.py` | the solution from the chapter |
| `run_exercise.py` | the harness: drives the solution and checks the outcome |

## Run it

```bash
cd chapter15/exercise_1_implementing_a_secure_timeout_boun/exercise/files
python3 run_exercise.py
```

`01_sandbox.py` only defines the executor; its test calls are commented out. The harness drives four snippets — success, runtime error, `sys.exit(3)` and a timeout — and exits non-zero if any branch lands in the wrong bucket.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The command was `["python", ...]`, which is not on `PATH` on macOS or in the container; it now uses `sys.executable`.
- The timeout case costs the listing's own five seconds, which is the point being demonstrated.
- Standard library plus `pydantic`; offline. The sketch printed in the exercise text is book-only because it assumes the classes from the exercise above.
