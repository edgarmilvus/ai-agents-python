# Example 1 — the agentic loop

## What it does

A research agent that is given a goal and nothing else. Each iteration it sends its memory — goal, action history, current state — to the model, receives a JSON decision with `next_action` and `goal_achieved`, and either executes the action or returns the synthesis.

## The listings

| file | what it is |
| --- | --- |
| `01_agentic_loop_research.py` | the listing: the OODA loop as a `while` loop over a JSON contract |
| `run_agentic_loop.py` | the harness: a scripted client, the same loop, assertions on every turn |

## Run it

```bash
cd chapter1/basic_code_example/example/files
python3 run_agentic_loop.py
```

This runs the harness rather than the listing, because the listing is the chapter's only one that calls a model: the harness replaces the client with a scripted one and drives the same loop offline. It prints one verdict line and exits non-zero if an assertion fails; the listing command is in **Notes**.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/trace.json` | the goal, the three decisions, the two execution results and the final summary |

## Notes

- Running `01_agentic_loop_research.py` itself calls a model and needs `OPENAI_COMPATIBLE_API_KEY`; the harness does not.
- `OPENAI_COMPATIBLE_BASE_URL` defaults to `https://openrouter.ai/api/v1` and `OPENAI_COMPATIBLE_MODEL` to `~deepseek/deepseek-flash-latest`.
- The listing sleeps 0.5 s after each execution; the harness makes no network call and runs in about two seconds.
