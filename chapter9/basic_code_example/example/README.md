# Example 1 — structured critique

## What it does

Four reviewers score one artifact against a schema: score 1-5, a pass/fail verdict and a justification. One reviewer sends an invalid score and the schema rejects it before consensus.

## The listings

| file | what it is |
| --- | --- |
| `01_structured_critique.py` | the listing: schema, simulated reviews, consensus and the failure |
| `run_exercise.py` | the harness: checks the reviews and the rejection |

## Run it

```bash
cd chapter9/basic_code_example/example/files
python3 01_structured_critique.py
```

The listing is the run: it prints each critique and the validation failure. `run_exercise.py` asserts the reviews and the rejection, and exits non-zero if an out-of-range score is accepted.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Pydantic only, offline.
- The mock Pydantic model stores only the fields it is given: a missing key reaches the validator, which names it, instead of dying with a TypeError from the constructor.
