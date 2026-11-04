# Exercise 4 — the unified persistent agent

## What it does

All four exercises in one agent: configuration, async history, a simplified vector store and the retrieval that makes the second interaction remember the first.

## The listings

| file | what it is |
| --- | --- |
| `01_unified_persistent_agent.py` | the solution: the unified agent |
| `run_unified_agent.py` | the harness: checks the interactions and the recall |

## Run it

```bash
cd chapter10/exercise_4_the_unified_persistent_agent_chall/exercise/files
python3 01_unified_persistent_agent.py
```

The listing is the run: it prints each interaction and the semantic recall. `run_unified_agent.py` asserts the counters and the retrieval, and exits non-zero if an interaction loses the persisted state.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of interactions |

## Notes

- Standard library only, offline.
- Exercises 10.4.1 to 10.4.3 have no listings of their own: this block is their combined implementation, and the book says so.
