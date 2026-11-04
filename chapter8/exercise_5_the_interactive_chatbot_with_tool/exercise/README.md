# Exercise 5 — the chatbot with retries

## What it does

A chatbot that retries a failing tool: a failed call is routed back to the tool executor with the error in the state, and the retry count caps the loop.

## The listings

| file | what it is |
| --- | --- |
| `01_chatbot_retries.py` | the solution from the chapter |
| `run_graph.py` | the harness: seeds the run and checks the outcome |

## Run it

```bash
cd chapter8/exercise_5_the_interactive_chatbot_with_tool/exercise/files
python3 01_chatbot_retries.py
```

The listing is the run: it prints the retry and the final answer. `run_graph.py` asserts the successful calculation and exits non-zero if the tool never answers.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed and the printed length |

## Notes

- Needs `langgraph`; runs offline.
- The random parts are seeded by the harness.
