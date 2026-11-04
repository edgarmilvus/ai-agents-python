# Exercise 3 — persistent research logging

## What it does

The research run is persisted: a SQLAlchemy model, a session per write, and a verification query that reads the last five runs back.

## The listings

| file | what it is |
| --- | --- |
| `01_hint.py` | the schema hint from the exercise |
| `02_exercise_3_persistent_logging.py` | the working version: model, sessions, logging and verification |
| `run_persistent_logging.py` | the harness: runs three writes and reads the database back |

## Run it

```bash
cd chapter5/exercise_3_persistent_research_logging_intera/exercise/files
python3 02_exercise_3_persistent_logging.py
```

The listing is the run: it logs three runs to SQLite and prints the verification query. `run_persistent_logging.py` reads the database back and exits non-zero if a run is missing; `01_hint.py` is the schema hint from the exercise.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the row count and the database file name |

## Notes

- Needs `sqlalchemy`; runs offline.
- The script deletes its database on start; the engine has to be disposed first, or SQLite writes through a deleted file and reports a read-only database.
