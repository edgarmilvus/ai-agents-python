# Exercise 4 — semantic review scoring

## What it does

Each critique's rationale is embedded and compared with the task vector; similarity boosts the critic's weight before consensus.

## The listings

| file | what it is |
| --- | --- |
| `01_semantic_review.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing (and the scaffold, where needed) |

## Run it

```bash
cd chapter9/exercise_4_interactive_challenge_semantic_rev/exercise/files
python3 run_exercise.py
```

`01_semantic_review.py` assumes the chapter's unified scaffold, so the harness composes the two published blocks and runs the result. It exits non-zero if the semantic adjustment stops being applied.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The exercise passes its own `task_vector=`; the scaffold's signature accepted only the module constant before.
