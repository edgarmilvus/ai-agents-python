# Example 2 — the research graph

## What it does

A verifier/refiner loop around a mock search tool: the verifier accepts or rejects the result, the refiner rewrites the query, and the counter caps the cycle.

## The listings

| file | what it is |
| --- | --- |
| `01_research_graph.py` | the listing: state, three nodes, router and graph |
| `run_research_graph.py` | the harness: a scripted model and the two-iteration cycle |

## Run it

```bash
cd chapter8/advanced_application_script/example/files
python3 run_research_graph.py
```

`01_research_graph.py` needs a key and a provider, so the harness scripts the model and runs the same graph. It writes `output/result.json` and exits non-zero if the cycle stops refining the query or the iteration limit is ignored.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the iterations and the refined query |

## Notes

- Needs `langgraph` and `langchain-openai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The model is asked two different questions (verify, refine) through the same client, which is why the harness scripts three answers in order.
