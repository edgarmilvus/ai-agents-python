# Exercise 1 — structured validators

## What it does

A schema with strict types and a score range, and three payloads: one valid, one out of range, one missing a field.

## The listings

| file | what it is |
| --- | --- |
| `01_pydantic_validators.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing (and the scaffold, where needed) |

## Run it

```bash
cd chapter9/exercise_1_enforcing_structured_feedback_with/exercise/files
python3 01_pydantic_validators.py
```

The listing is the run: it parses a valid payload and rejects two invalid ones. `run_exercise.py` asserts all three outcomes and exits non-zero if a missing field stops reaching the validator.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The mock Pydantic model stores only the fields it is given: a missing key reaches the validator, which names it, instead of dying with a TypeError from the constructor.
