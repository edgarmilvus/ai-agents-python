# Exercise 4 — structured output

## What it does

The same decision as free-form thought/action text and as a Pydantic object: the JSON version is shorter, and it validates, which is what removes the retry cost.

## The listings

| file | what it is |
| --- | --- |
| `01_structured_output.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter19/exercise_4_interactive_challenge_enforcing_st/exercise/files
python3 01_structured_output.py
```

The listing is the run: it compares the token cost of a free-form answer with the same answer as JSON, then validates the JSON against the schema. The harness asserts the parse and the fields.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The saving on this sentence is under the 30% target, so the listing prints a warning instead of failing — the target depends on how verbose the free-form answer is.
- Validation is the second half of the saving: a malformed answer costs a retry, and the schema makes that outcome impossible.
- Offline: the model calls are simulated or mocked, and `tiktoken` supplies the token counts.
