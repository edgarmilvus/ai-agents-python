# Example 3 — the exercise scripts

## What it does

The four exercises in one block: a layered sanitizer, a strict tool-call validator, a time-budget context manager and a RAG guardrail that classifies intent before spending a retrieval.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_scripts.py` | the listing: four exercises and their demos |
| `run_exercise_scripts.py` | the harness: checks each demo's conclusion |

## Run it

```bash
cd chapter17/worked_example_consolidated_python_code_block/example/files
python3 01_exercise_scripts.py
```

The listing is the run: all four exercises demonstrate themselves. The harness checks each conclusion, including the budget's documented limitation — a context manager reports an overrun on exit, it cannot interrupt the block.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of exercises it checked |

## Notes

- The exercise-1 demo was a single line of `$` padding with no closing quote: the file did not parse. It now has four cases — safe, blacklisted, too short and repetitive padding.
- The exercise-3 budget checks the clock in `__exit__`, so "Operation finished" prints even when the budget is blown. The class and the demo say so; the preemptive version is example 2.
- The off-topic demo used a weather question the classifier did not know; it now uses a joke, which is in the rule set, so all three classifications appear.
