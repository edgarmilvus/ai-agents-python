# Exercise 1 — the asynchronous budget

## What it does

A context manager that adds up tokens as calls are made and raises `TokenBudgetExceededError` as soon as the total would cross the limit, so the next call never happens.

## The listings

| file | what it is |
| --- | --- |
| `01_async_budget.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter19/exercise_1_asynchronous_token_budget_manager/exercise/files
python3 01_async_budget.py
```

The listing is the run: one context finishes inside the budget, one is stopped at the breach. The harness asserts both and that the call after the breach never executes.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The breach is checked before the call is charged, so the ledger stops at 50 of a 100-token budget rather than at 105.
- `__aexit__` reports the final usage and lets the exception propagate; it does not swallow it.
- Offline: the model calls are simulated or mocked, and `tiktoken` supplies the token counts.
