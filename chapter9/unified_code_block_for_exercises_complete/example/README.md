# Example 4 — the complete exercise block

## What it does

The same pipeline assembled end to end: schema, critics, weighted consensus with semantic scoring, persistence and the read-back that proves the audit trail.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_complete.py` | the complete implementation |
| `run_exercise.py` | the harness: checks the commit and the read-back |

## Run it

```bash
cd chapter9/unified_code_block_for_exercises_complete/example/files
python3 01_exercise_complete.py
```

The listing is the run: it prints the full pipeline and the persisted rows. `run_exercise.py` asserts the commit and the read-back, and exits non-zero if the audit trail loses a field.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- This is the reference implementation the five solutions converge on.
