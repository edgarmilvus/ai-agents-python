# Example 3 — the exercise scaffold

## What it does

The shared scaffold for the five exercises: a mock Pydantic base, the critique schema, weighted consensus and a mock database, all runnable without external libraries.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_scaffold.py` | the scaffold the exercises compose |
| `run_exercise.py` | the harness: runs the scaffold's own demonstration |

## Run it

```bash
cd chapter9/unified_code_block_for_exercises_scaffold/example/files
python3 01_exercise_scaffold.py
```

The listing is the run: it exercises the mock schema and the mock database. `run_exercise.py` asserts the commit and the stored records, and exits non-zero if the mock stops validating.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The mock Pydantic model stores only the fields it is given: a missing key reaches the validator, which names it, instead of dying with a TypeError from the constructor.
- `calculate_weighted_consensus` now takes `task_vector=`: exercise 4 scores against its own vector instead of relying on the module constant.
