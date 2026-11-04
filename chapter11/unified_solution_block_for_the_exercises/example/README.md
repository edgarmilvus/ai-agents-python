# Example 3 — the unified solution

## What it does

The five exercises answered in one block: adaptive chunking, metadata filtering, a self-refining loop, recency weighting and the multi-vector router.

## The listings

| file | what it is |
| --- | --- |
| `01_unified_solution.py` | the combined solution |
| `run_unified_solution.py` | the harness: routes a code query and a documentation query |

## Run it

```bash
cd chapter11/unified_solution_block_for_the_exercises/example/files
python3 01_unified_solution.py
```

The listing is the run: it prints each routed query and the documents it retrieved. `run_unified_solution.py` asserts both stores and exits non-zero if a route returns nothing.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of routed queries |

## Notes

- Standard library only, offline.
- Python before 3.12 forbids a backslash inside an f-string expression: the chunk preview is built on its own line.
