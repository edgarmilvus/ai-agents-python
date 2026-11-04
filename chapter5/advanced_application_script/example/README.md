# Example 2 — the research brief

## What it does

The same architecture with a tool: the agent searches a corpus, then writes a structured executive brief to Markdown. The process is sequential because there is one agent and one task.

## The listings

| file | what it is |
| --- | --- |
| `01_advanced_application_script.py` | the listing: search tool, agent, task, crew and file output |
| `run_advanced_crew.py` | the harness: scripted model, the tool exercised, the brief checked |

## Run it

```bash
cd chapter5/advanced_application_script/example/files
python3 run_advanced_crew.py
```

`01_advanced_application_script.py` needs a key and a provider, so the harness scripts the model and runs the same crew and tool. It writes `output/result.json` and the brief under `output/`, and exits non-zero if the tool or the file stops working.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model call count and the brief's length |
| `output/executive_brief.md` | the Markdown file the crew writes |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The search is a local `BaseTool` over a curated corpus: a production agent would call Tavily, which needs a second provider key and the network.
- `kickoff()` returns a `CrewOutput`, not a string: the listing converts it once and writes that text, which is why the file is no longer empty.
