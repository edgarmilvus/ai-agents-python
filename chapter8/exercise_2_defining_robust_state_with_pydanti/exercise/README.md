# Exercise 2 — a robust state

## What it does

A Pydantic schema in the state: invalid items are rejected by validation, logged, and the graph continues with the rest.

## The listings

| file | what it is |
| --- | --- |
| `01_robust_state.py` | the solution from the chapter |
| `run_graph.py` | the harness: seeds the run and checks the outcome |

## Run it

```bash
cd chapter8/exercise_2_defining_robust_state_with_pydanti/exercise/files
python3 01_robust_state.py
```

The listing is the run: it processes five items and prints the one the schema rejected. `run_graph.py` asserts the rejection and exits non-zero if an invalid item is accepted.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed and the printed length |

## Notes

- Needs `langgraph`; runs offline.
- The random parts are seeded by the harness.
