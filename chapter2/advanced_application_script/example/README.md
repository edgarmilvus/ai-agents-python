# Example 2 — the strategic analyst

## What it does

The same ReAct loop with a policy in the prompt: retrieve internal knowledge, call the market-data tool, reflect on both, then recommend. The RAG context is injected before the run rather than fetched by the agent.

## The listings

| file | what it is |
| --- | --- |
| `01_strategic_analyst.py` | the listing: RAG simulation, one tool, a four-stage prompt and the executor |
| `run_strategic_analyst.py` | the harness: a scripted model, the tool observation, the final answer |

## Run it

```bash
cd chapter2/advanced_application_script/example/files
python3 run_strategic_analyst.py
```

The harness scripts the model, keeps the listing's RAG injection and drives the single tool call. It writes `output/run.json` and exits non-zero if the tool's observation never reaches the agent.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/run.json` | the retrieved context, whether the observation arrived and the final answer |

## Notes

- Needs `langchain-classic`, `langchain-community` and `langchain-openai` from `requirements.txt`.
- Running a listing that builds a client needs `OPENAI_COMPATIBLE_API_KEY`; the harnesses do not.
- `OPENAI_COMPATIBLE_BASE_URL` defaults to `https://openrouter.ai/api/v1` and `OPENAI_COMPATIBLE_MODEL` to `~deepseek/deepseek-flash-latest`.
- The prompt's four stages are in `SYSTEM_PROMPT`; the executor fills the ReAct slots on every step.
