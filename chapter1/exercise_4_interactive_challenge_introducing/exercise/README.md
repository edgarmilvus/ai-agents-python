# Exercise 4 — a planning layer in front of RAG

## What it does

A RAG pipeline with a step in front of it. The planner decides whether the query needs retrieval at all and, if it does, rewrites it into the query the vector store receives. Only the second decision reaches the retrieval path.

## The listings

| file | what it is |
| --- | --- |
| `01_planning_layer_rag.py` | the solution: a planning template, a simulated planner, and two terminal paths |
| `run_planning_layer.py` | the harness: a direct question, a history question and an unrecognised one |

## Run it

```bash
cd chapter1/exercise_4_interactive_challenge_introducing/exercise/files
python3 01_planning_layer_rag.py
```

The listing is the run: it plans two queries, follows both branches and prints each answer. The harness adds an unrecognised query and exits non-zero if the retriever receives an unrefined query or a direct question reaches it at all.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/planning.json` | the planner output for each query, and the answer produced on each path |

## Notes

- No dependencies beyond the standard library, no network.
- The planner is rule-based on purpose: it stands in for the model call, so the exercise is about the control flow, not about prompting.
- The RAG and direct paths are terminal; nothing loops back into planning.
