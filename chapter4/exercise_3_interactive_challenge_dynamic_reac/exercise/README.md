# Exercise 3 — dynamic ReAct

## What it does

Self-correction driven by the quality of an observation: the first search is too broad, the loop narrows the query, and the second observation grounds the answer.

## The listings

| file | what it is |
| --- | --- |
| `01_dynamic_react.py` | the solution: a simulated trace with two observations |
| `run_dynamic_react.py` | the harness: checks the refinement happened before the answer |

## Run it

```bash
cd chapter4/exercise_3_interactive_challenge_dynamic_reac/exercise/files
python3 01_dynamic_react.py
```

The listing is the run: it prints the three steps and the refined answer. `run_dynamic_react.py` asserts that the loop refines its query and exits non-zero if the second observation never arrives.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of steps and observations in the trace |

## Notes

- No dependencies beyond the standard library, no network.
- The trace is simulated; the lesson is the control flow, not the search.
