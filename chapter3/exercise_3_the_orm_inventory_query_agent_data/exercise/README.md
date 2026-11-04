# Exercise 3 — the ORM inventory query

## What it does

A SQLAlchemy query tool with three optional filters. Every row is serialised for the model, the session is closed in a `finally`, and an empty result is a sentence rather than an exception.

## The listings

| file | what it is |
| --- | --- |
| `01_orm_inventory_agent.py` | the solution from the chapter |
| `run_orm_inventory.py` | the harness: composes the mock services with this listing and calls the tool |

## Run it

```bash
cd chapter3/exercise_3_the_orm_inventory_query_agent_data/exercise/files
python3 run_orm_inventory.py
```

`01_orm_inventory_agent.py` defines the query tool over the seeded database. `run_orm_inventory.py` runs each filter and exits non-zero if a row escapes it.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the counts and names returned by each filter |

## Notes

- Runs offline and deterministically; no key is read.
- Needs `sqlalchemy` only where the mock services are composed in.
