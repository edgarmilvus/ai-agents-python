# Example 3 — the exercise scripts

## What it does

The four exercises' code in one block: a traced extraction root run, an inventory tool that must reject `"150 units"`, a cost comparison between two model configurations, and two research policies with different prompts.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_scripts.py` | the listing: client, model, tools, four functions |
| `run_exercise_scripts.py` | the harness: drives all four with an in-memory client |

## Run it

```bash
cd chapter16/worked_example_the_exercise_scripts/example/files
python3 run_exercise_scripts.py
```

`01_exercise_scripts.py` only defines the client, the model and the four functions; every demo is commented out. The harness supplies the client and one scripted model per `ChatOpenAI(...)` call, then drives all four exercises.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | how many root runs reached the client |

## Notes

- The prompts had no `agent_scratchpad` placeholder, so `create_openai_tools_agent` refused to build a single agent. All of them have one now.
- `agent_executor.agent.prompt` does not exist on the agent this creator returns; the prompt is now built by `build_inventory_prompt()` and shared by both configurations.
- The extraction chain returned an `AIMessage`, not a string, because it had no parser; `StrOutputParser` closes it.
