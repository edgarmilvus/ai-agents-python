# Example 2 — a traced tool-calling agent

## What it does

Two tools — a news search and a growth calculation — bound to one executor. Each query is routed by the model, and the trace is what shows which tool fired and with what arguments.

## The listings

| file | what it is |
| --- | --- |
| `01_traced_agent.py` | the listing: tools, prompt, executor, two runs |
| `run_traced_agent.py` | the harness: a scripted conversation, one path per query |

## Run it

```bash
cd chapter16/advanced_application_script/example/files
python3 run_traced_agent.py
```

`01_traced_agent.py` binds the tools and sends two queries through the executor, which needs a model key. The harness scripts the model so the first query takes the search path and the second the calculation path, then checks both answers and both tool calls.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the two final answers |

## Notes

- The listing paired a ReAct prompt with `create_react_agent` and a `MessagesPlaceholder` prompt, which cannot build an agent. It now uses `create_openai_tools_agent`, the creator that matches its prompt.
- `create_openai_tools_agent` binds tools through `bind(tools=...)`, not `bind_tools`, which is why the fake is scripted with explicit tool-call messages.
