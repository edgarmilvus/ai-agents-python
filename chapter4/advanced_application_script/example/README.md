# Example 2 — the ReAct agent

## What it does

A ReAct loop with two tools: one fetches a mock price, the other computes a momentum score from a JSON payload. The prompt spells out Thought, Action, Observation and Final Answer, and the executor enforces the loop.

## The listings

| file | what it is |
| --- | --- |
| `01_react_agent.py` | the listing: tools, ReAct prompt, agent and executor |
| `run_react_agent.py` | the harness: three scripted decisions, both tools exercised |

## Run it

```bash
cd chapter4/advanced_application_script/example/files
python3 run_react_agent.py
```

`01_react_agent.py` needs a key and a provider, so the harness scripts three decisions and runs the same two tools. It writes `output/run.json` and exits non-zero if a tool is skipped or the final answer is not the executor's.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/run.json` | the final answer, the tools called and the model |

## Notes

- Needs `langchain-classic`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- A ReAct loop hands a tool one string, so the momentum tool takes a JSON object and parses it. Two float arguments would arrive unparsed.
- The prompt carries `{tools}`, `{tool_names}` and `{agent_scratchpad}`: without them `create_react_agent` refuses the template.
