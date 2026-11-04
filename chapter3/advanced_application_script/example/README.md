# Example 2 — the market analyst

## What it does

A structured-chat agent with two tools: one reads a mocked market API, the other appends the record to a JSON file. The model chooses the tools and the executor runs them in order.

## The listings

| file | what it is |
| --- | --- |
| `01_market_analyst.py` | the listing: two Pydantic-schemed tools, a prompt and the executor |
| `run_market_analyst.py` | the harness: a scripted model and a fresh history file per run |

## Run it

```bash
cd chapter3/advanced_application_script/example/files
python3 run_market_analyst.py
```

`01_market_analyst.py` needs a key and a provider, so the harness scripts the model and runs the same two tools. It writes `output/run.json` and the history file under `output/`, and exits non-zero if a tool is skipped or the record is wrong.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/run.json` | the answer, the history record and the model used |
| `output/market_history.json` | the file the logging tool appends to |

## Notes

- Needs `langchain-classic` and `langchain-openai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The prompt carries `{tools}` and `{tool_names}` and interpolates `agent_scratchpad` as text: a message placeholder would receive a string and fail.
- The harness deletes the history file before each run, so the record count is meaningful.
