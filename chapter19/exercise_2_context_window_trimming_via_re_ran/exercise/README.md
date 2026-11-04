# Exercise 2 — context trimming

## What it does

Ten documents, two of which contain the answer. A keyword pass stands in for semantic re-ranking, and only the relevant documents plus one supporting document reach the model.

## The listings

| file | what it is |
| --- | --- |
| `01_rerank_trimming.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter19/exercise_2_context_window_trimming_via_re_ran/exercise/files
python3 01_rerank_trimming.py
```

The listing is the run: it trims ten documents and prints the saving. The harness reads that number and fails if it drops below the 60% the exercise asks for.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- Keeping two supporting documents gave 51%, so the assertion failed every run. One supporting document gives 60.27% — the exercise's own goal.
- The solution was an excerpt with no imports; it now carries the token-counting setup it uses.
- Offline: the model calls are simulated or mocked, and `tiktoken` supplies the token counts.
