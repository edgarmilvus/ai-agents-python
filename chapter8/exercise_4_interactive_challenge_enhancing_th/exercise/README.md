# Exercise 4 — the financial analyst

## What it does

The analyst graph extended with a mandatory risk section and a review gate before the report is finalised.

## The listings

| file | what it is |
| --- | --- |
| `01_financial_analyst.py` | the solution from the chapter |
| `run_graph.py` | the harness: seeds the run and checks the outcome |

## Run it

```bash
cd chapter8/exercise_4_interactive_challenge_enhancing_th/exercise/files
python3 01_financial_analyst.py
```

The listing is the run: it prints each node and the finalised report. `run_graph.py` asserts the risk section and exits non-zero if the graph stops before finalising.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed and the printed length |

## Notes

- Needs `langgraph`; runs offline.
- The random parts are seeded by the harness.
