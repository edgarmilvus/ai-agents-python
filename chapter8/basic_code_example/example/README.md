# Example 1 — the cyclic graph

## What it does

Three nodes and one conditional edge: generate a title, check the five-word constraint, and loop back to generation until it holds. The state carries an additive counter and the decision the router reads.

## The listings

| file | what it is |
| --- | --- |
| `01_cyclic_graph.py` | the listing: state, nodes, router and graph |
| `run_cyclic_graph.py` | the harness: checks the loop, the constraint and the exit |

## Run it

```bash
cd chapter8/basic_code_example/example/files
python3 01_cyclic_graph.py
```

The listing is the run: it prints the failed check, the loop and the successful second pass. `run_cyclic_graph.py` asserts the same two iterations and exits non-zero if the loop stops routing back.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the iteration count and the final title |

## Notes

- Needs `langgraph`; runs offline.
- A node returns a state update, never a bare string: the decision is written to the state and the conditional edge reads it. Returning `"refine"` from a node raises `InvalidUpdateError`.
- `add_conditional_edges` takes `path_map`, not the older `output_map`.
