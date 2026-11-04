# Example 2 — the hierarchical crew

## What it does

A CrewAI crew with two workers, a manager, and a synthesis task that depends on both worker outputs. The process is hierarchical, so the manager delegates rather than executing tasks itself.

## The listings

| file | what it is |
| --- | --- |
| `01_hierarchical_crew.py` | the listing: manager, two workers, three tasks, one crew |
| `run_hierarchical_crew.py` | the harness: a scripted CrewAI model and the crew's shape |

## Run it

```bash
cd chapter6/advanced_application_script/example/files
python3 run_hierarchical_crew.py
```

`01_hierarchical_crew.py` needs a key and a provider, so the harness scripts CrewAI's model and runs the same crew. It writes `output/result.json` and exits non-zero if the manager is listed among the agents or the search tool stops answering.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the brief, the model call count and the agent roles |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- CrewAI 1.x requires the manager to be named by `manager_agent` and *not* listed in `agents`; the harness asserts that shape.
- The research tool is a local `BaseTool` over a curated corpus; a production crew would call Serper or Tavily.
- Live, this is the slowest listing in the volume: 288 s on `deepseek-flash`, because
  the manager delegates every step. The harness scripts the model, so the suite
  stays under a minute.
