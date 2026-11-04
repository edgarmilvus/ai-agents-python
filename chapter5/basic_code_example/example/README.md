# Example 1 — the research assistant

## What it does

A single CrewAI agent with a role, a goal and a backstory, one task with an explicit output contract, and a crew that runs it. The LLM is configured once, for an OpenAI-compatible gateway.

## The listings

| file | what it is |
| --- | --- |
| `01_basic_research_agent.py` | the listing: LLM, agent, task and crew |
| `run_basic_crew.py` | the harness: a scripted CrewAI model, the same crew |

## Run it

```bash
cd chapter5/basic_code_example/example/files
python3 run_basic_crew.py
```

`01_basic_research_agent.py` needs a key and a provider, so the harness scripts CrewAI's model and runs the same crew. It writes `output/result.json` and exits non-zero if the task stops carrying the topic or the agent stops using the configured model.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the report, the number of model calls and the model name |

## Notes

- Needs `crewai` from `requirements.txt`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The harness sets a placeholder key because the listings check for one, then substitutes the model: no call leaves the machine.
- CrewAI 1.x validates `verbose` as a boolean; the listing passes `True`, not `2`.
