# Exercise 1 — the format validator

## What it does

A validator that reads the raw output, not the instruction: it accepts a valid profile and rejects a missing key and an illegal status code.

## The listings

| file | what it is |
| --- | --- |
| `01_format_validator.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the outcome |

## Run it

```bash
cd chapter12/exercise_1_the_format_validator_reflection_lo/exercise/files
python3 01_format_validator.py
```

The listing is the run: it accepts one payload and rejects two with the reason. `run_exercise.py` asserts all three and exits non-zero if the validator stops reading the raw output.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The prompt carries the schema, so a validator that scans the whole prompt accepts everything; the mock now isolates the `RAW OUTPUT:` section.
