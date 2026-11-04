# Exercise 1 — research with confidence

## What it does

A research loop that stops on a confidence threshold rather than a fixed count: each attempt collects documents, scores them, and the router exits when the score is high enough.

## The listings

| file | what it is |
| --- | --- |
| `01_research_confidence.py` | the solution from the chapter |
| `run_graph.py` | the harness: seeds the run and checks the outcome |

## Run it

```bash
cd chapter8/exercise_1_the_iterative_research_and_confide/exercise/files
python3 01_research_confidence.py
```

The listing is the run: it prints the confidence after each attempt and the final state. `run_graph.py` asserts the stopping condition and exits non-zero if the loop keeps going past it.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed and the printed length |

## Notes

- Needs `langgraph`; runs offline.
- The random parts are seeded by the harness.
