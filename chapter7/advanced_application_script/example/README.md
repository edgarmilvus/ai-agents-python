# Example 2 — the marketing crew

## What it does

Three specialists with one delegating agent: a researcher, a writer and a strategist who can send work back. The crew shares one search tool and one model.

## The listings

| file | what it is |
| --- | --- |
| `01_marketing_crew.py` | the listing: three agents, tasks and the crew |
| `run_marketing_crew.py` | the harness: scripted model, the tool and the delegation flag |

## Run it

```bash
cd chapter7/advanced_application_script/example/files
python3 run_marketing_crew.py
```

`01_marketing_crew.py` needs a key and a provider, so the harness scripts the model and runs the same crew and tool. It writes `output/result.json` and exits non-zero if the delegation flag or the search tool disappears.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the campaign result, the call count and the roles |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The search tool is a local `BaseTool` over a curated corpus; Serper or Tavily would replace the class, not the agents.
