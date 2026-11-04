# Exercise 4 — robust configuration

## What it does

A command-line entry point that checks `sys.argv` before the agent starts: a missing `--task-id` produces an LLM-written usage guide instead of a traceback.

## The listings

| file | what it is |
| --- | --- |
| `02_robust_config.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the outcome |

## Run it

```bash
cd chapter12/exercise_4_interactive_challenge_robust_confi/exercise/files
python3 02_robust_config.py
```

The listing is the run: it prints the usage guide for a missing argument and starts cleanly with one. `run_exercise.py` asserts both paths and exits non-zero if the guide stops being produced; `01_agent_runner.py` is the starter from the exercise.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The usage-guide mock now triggers on `usage guide`, which is what the prompt asks for.
