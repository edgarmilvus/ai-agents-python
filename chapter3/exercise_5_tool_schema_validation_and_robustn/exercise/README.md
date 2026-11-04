# Exercise 5 — schema validation

## What it does

A hashing tool that validates before it computes: an unsupported algorithm is rejected with the list of supported ones, and an oversized input is refused with the limit named.

## The listings

| file | what it is |
| --- | --- |
| `01_schema_validation_agent.py` | the solution from the chapter |
| `run_schema_validation.py` | the harness: composes the mock services with this listing and calls the tool |

## Run it

```bash
cd chapter3/exercise_5_tool_schema_validation_and_robustn/exercise/files
python3 run_schema_validation.py
```

`01_schema_validation_agent.py` defines the hashing tool. `run_schema_validation.py` checks the whitelist and the size guard and exits non-zero if an unsupported algorithm is hashed anyway.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the digests and both rejection messages |

## Notes

- Runs offline and deterministically; no key is read.
- Needs `sqlalchemy` only where the mock services are composed in.
