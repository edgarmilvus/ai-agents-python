# Exercise 4 — schema validation

## What it does

A Pydantic model in front of the final answer: the summary must carry findings, a confidence and a tool count, and the confidence is constrained to 0-100.

## The listings

| file | what it is |
| --- | --- |
| `01_schema_starter.py` | the schema skeleton the exercise starts from |
| `02_schema_agent.py` | the validated version, with the range constraint on confidence |
| `run_schema_agent.py` | the harness: valid and invalid outputs, both checked |

## Run it

```bash
cd chapter4/exercise_4_structured_react_output_via_pydant/exercise/files
python3 02_schema_agent.py
```

The listing is the run: it validates the answer against the schema and prints the JSON. `run_schema_agent.py` checks the same schema and exits non-zero if an out-of-range confidence is accepted; `01_schema_starter.py` is the skeleton it grew from.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the validated summary |

## Notes

- Needs `pydantic` from `requirements.txt`.
- `confidence_score` is `Field(ge=0, le=100)`: without the bound, 150 validates and the schema proves nothing.
