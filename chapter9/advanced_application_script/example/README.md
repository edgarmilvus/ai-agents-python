# Example 2 — the critique loop

## What it does

Three specialist critics review a draft, their scores are weighted into a consensus, and the consolidated advice feeds the next revision until the score passes.

## The listings

| file | what it is |
| --- | --- |
| `01_critique_loop.py` | the listing: critics, weighted consensus and the refinement cycle |
| `run_exercise.py` | the harness: checks the aggregation and the cycle |

## Run it

```bash
cd chapter9/advanced_application_script/example/files
python3 01_critique_loop.py
```

The listing is the run: it prints each cycle, the consolidated advice and the verdict. `run_exercise.py` asserts the aggregation and exits non-zero if the loop stops reporting a score.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Pydantic only, offline.
- The weights and the critic prompts are module-level data, so a new criterion is an entry, not a branch.
