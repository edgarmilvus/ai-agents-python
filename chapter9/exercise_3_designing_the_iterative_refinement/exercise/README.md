# Exercise 3 — the refinement loop

## What it does

A generator, a critique group and a consensus step in a loop that stops at a score threshold or an iteration cap, carrying the advice into the next revision.

## The listings

| file | what it is |
| --- | --- |
| `01_refinement_loop.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing (and the scaffold, where needed) |

## Run it

```bash
cd chapter9/exercise_3_designing_the_iterative_refinement/exercise/files
python3 run_exercise.py
```

`01_refinement_loop.py` assumes the chapter's unified scaffold, so the harness composes the two published blocks and runs the result. It exits non-zero if the loop stops terminating or loses its final score.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The loop prints its final score and iteration count, which is what the harness asserts.
