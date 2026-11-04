# Exercise 3 — code refinement

## What it does

A generator, a test runner and a debugger in a loop: the failure report becomes the next prompt, and the graph exits on the first pass.

## The listings

| file | what it is |
| --- | --- |
| `01_code_refinement.py` | the solution from the chapter |
| `run_graph.py` | the harness: seeds the run and checks the outcome |

## Run it

```bash
cd chapter8/exercise_3_the_code_refinement_and_self_corre/exercise/files
python3 01_code_refinement.py
```

The listing is the run: it fails, debugs and passes on the third attempt. `run_graph.py` asserts the final PASS and exits non-zero if the loop stops before it.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed and the printed length |

## Notes

- Needs `langgraph`; runs offline.
- The random parts are seeded by the harness.
