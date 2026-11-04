# Example 1 — the self-correcting architecture

## What it does

A three-node loop: generate a profile, validate it against a schema, and re-plan with the validation error when it fails. The first output is missing a key; the second is accepted.

## The listings

| file | what it is |
| --- | --- |
| `01_self_correcting_architecture.py` | the listing: nodes, validation and the loop |
| `run_exercise.py` | the harness: checks the rejection and the correction |

## Run it

```bash
cd chapter12/basic_code_example/example/files
python3 01_self_correcting_architecture.py
```

The listing is the run: it prints the rejected first attempt, the reflection and the accepted second. `run_exercise.py` asserts the correction and exits non-zero if the loop accepts the malformed output.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The mock model is keyed on the prompt's wording; a trigger that misses returns an empty string and the loop silently misbehaves.
