# Example 1 — the sanitization layer

## What it does

A deny-list, a normalisation step and a word-boundary regex. Four inputs go through the gate: a benign query, a direct injection, the same injection in mixed case, and a sentence containing "systematic" to show why `\b` matters.

## The listings

| file | what it is |
| --- | --- |
| `01_sanitization_layer.py` | the listing: the deny-list, the check and four cases |
| `run_sanitization.py` | the harness: reads the four verdicts and calls the check directly |

## Run it

```bash
cd chapter17/17_2_basic_code_example_implementing_a_keywor/example/files
python3 01_sanitization_layer.py
```

The listing is the run: four inputs go through the gate and each prints its verdict. The harness asserts all four and calls `sanitize_input` directly, so a case that stops blocking cannot hide behind a print statement.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | how many inputs were blocked |

## Notes

- The agent answer is a fixed string: the point of the listing is the gate, not the model behind it.
- "systematic" passes because `\b` bounds the keyword; without it, `system prompt` would match inside `systematic`.
- A deny-list is a first layer, not a solution: the chapter says so, and the next listing adds a budget and an output check.
