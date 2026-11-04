# Example 1 — the cost tracker

## What it does

An asynchronous wrapper around a simulated model call. Each call estimates its input and output tokens, prices them at the configured rates, and adds them to a cumulative ledger; the closing report is the agent's bill.

## The listings

| file | what it is |
| --- | --- |
| `01_cost_tracker.py` | the listing: rates, the tracker, three calls, the report |
| `run_cost_tracker.py` | the harness: checks the arithmetic and the total |

## Run it

```bash
cd chapter19/basic_code_example/example/files
python3 01_cost_tracker.py
```

The listing is the run: three simulated calls print their usage, their cost and the running total. The harness checks the arithmetic directly — rates per million tokens, one token per four characters — and that the three transactions add up to the reported total.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the total cost and the three transactions |

## Notes

- `_estimate_tokens` is a heuristic, not a tokenizer; the chapter says so and the pitfall section explains what it costs when the estimate is wrong.
- The rates are constants, not a bill: they are the multiplier the exercise is about.
- Every call is `await`ed, so the ledger updates in order and the report can sum them.
