# Example 3 — the exercise framework

## What it does

The shared infrastructure for the chapter's exercises: a mock LLM, a schema validator, the error classification, the usage guide and the tool-failure registry, demonstrated in one run.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_framework.py` | the framework and its demos |
| `run_exercise.py` | the harness: checks each demo it runs |

## Run it

```bash
cd chapter12/python_code_framework_for_exercises/example/files
python3 01_exercise_framework.py
```

The listing is the run: it prints the shared demos for exercises 1, 2, 4 and 5, with the validator and the handler registry. `run_exercise.py` asserts each and exits non-zero if a handler stops firing.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- Exercise 3's recursive loop is its own listing, not part of the framework's demo.
