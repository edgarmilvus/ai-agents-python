# Exercise 2 — hierarchical planning

## What it does

A Manager agent decomposes a goal into a JSON plan; an orchestrator executes each step against the tool it names, feeds one step's output into the next, and hands the results to a final synthesis.

## The listings

| file | what it is |
| --- | --- |
| `01_hierarchical_planner.py` | the solution from the chapter |
| `run_hierarchical_planner.py` | the harness: composes the boilerplate with this listing and asserts the result |

## Run it

```bash
cd chapter2/exercise_2_hierarchical_planning_and_decompos/exercise/files
python3 run_hierarchical_planner.py
```

`01_hierarchical_planner.py` assumes the chapter's boilerplate, so the harness composes the two published blocks and runs the result. It writes `output/result.json` and exits non-zero if a step loses its arguments or the synthesis stops quoting the tool result.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the final report, the manager's call count and the step log |

## Notes

- Runs offline and deterministically: the boilerplate's `MockLLM` answers, no key is read.
- The harness runs the two published blocks exactly as the book publishes them; neither file is copied or edited.
