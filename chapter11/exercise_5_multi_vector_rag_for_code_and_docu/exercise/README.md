# Exercise 5 — multi-vector RAG

## What it does

Two stores, one router: code queries go to a small-chunk code store, documentation queries to a paragraph store. The hint block is the whole mocked infrastructure for the five exercises.

## The listings

| file | what it is |
| --- | --- |
| `01_multi_vector_hint.py` | the hint: mock embeddings, documents, stores and the router |
| `run_multi_vector.py` | the harness: checks the exercises and the routing |

## Run it

```bash
cd chapter11/exercise_5_multi_vector_rag_for_code_and_docu/exercise/files
python3 01_multi_vector_hint.py
```

The listing is the run: it prints the chunking, the filtering and the routing decisions. `run_multi_vector.py` asserts the exercises and exits non-zero if the router stops selecting a store.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline: every external component is mocked.
- The metadata filter contains a datetime, so `json.dumps` needs `default=str`; without it the run dies before the router.
