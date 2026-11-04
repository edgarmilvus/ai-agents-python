# Example 2 — the autonomous job filter

## What it does

Selenium collects the job cards, a Pydantic schema pins the decision, and a prompt turns each posting into a parsed `JobMatchDecision`. The model is reached over the OpenAI-compatible endpoint named by `OPENAI_COMPATIBLE_BASE_URL`, with the model named by `OPENAI_COMPATIBLE_MODEL`.

## The listings

| file | what it is |
| --- | --- |
| `01_job_filter_agent.py` | the listing: schema, prompt, agent loop |
| `run_job_filter.py` | the harness: two scripted cards and a fake chat model |

## Run it

```bash
cd chapter14/advanced_application_script/example/files
python3 run_job_filter.py
```

`01_job_filter_agent.py` needs a key, a browser and a live job board, so the fence runs the harness: it scripts two job cards and one fake chat model, then checks that the matching posting is accepted and the other rejected.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the postings processed and the url visited |

## Notes

- The prompt, the `PydanticOutputParser` and the decision branch are the listing's; only the driver and the model are replaced.
- The listing raised at import when `OPENAI_API_KEY` was missing; it now reads `OPENAI_COMPATIBLE_API_KEY`, and the model and endpoint come from the environment.
- The parser failure path defaults to `is_match=False`, so a malformed answer skips a posting rather than crashing the run.
