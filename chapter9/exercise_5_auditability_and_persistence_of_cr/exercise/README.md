# Exercise 5 — the critique audit trail

## What it does

Every critique is written to a mock SQLAlchemy session with its score, verdict, rationale and refinement steps, and then read back.

## The listings

| file | what it is |
| --- | --- |
| `01_critique_audit.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing (and the scaffold, where needed) |

## Run it

```bash
cd chapter9/exercise_5_auditability_and_persistence_of_cr/exercise/files
python3 run_exercise.py
```

`01_critique_audit.py` assumes the chapter's unified scaffold, so the harness composes the two published blocks and runs the result. It exits non-zero if the audit rows are not committed.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The mock session commits and assigns ids, so the read-back order is the insertion order.
