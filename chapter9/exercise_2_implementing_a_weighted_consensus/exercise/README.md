# Exercise 2 — weighted consensus

## What it does

Critiques carry per-agent weights, the weighted average becomes the consensus score, and a critical-error flag vetoes the pass.

## The listings

| file | what it is |
| --- | --- |
| `01_weighted_consensus.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing (and the scaffold, where needed) |

## Run it

```bash
cd chapter9/exercise_2_implementing_a_weighted_consensus/exercise/files
python3 run_exercise.py
```

`01_weighted_consensus.py` assumes the chapter's unified scaffold, so the harness composes the two published blocks and runs the result. It exits non-zero if the consensus or the aggregated advice disappears.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The listing has no imports of its own: the scaffold supplies the typing names and the schema.
