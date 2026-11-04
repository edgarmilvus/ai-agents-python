# Example 1 — the sequential swarm

## What it does

Two roles and an orchestrator: the idea generator produces a structured motto, the formatter turns it into a client deliverable, and a second run shows what happens when QA refuses the handoff.

## The listings

| file | what it is |
| --- | --- |
| `01_sequential_swarm.py` | the listing: models, mock model, two agents, the orchestrator |
| `run_sequential_swarm.py` | the harness: checks delivery and the halt |

## Run it

```bash
cd chapter20/basic_code_example/example/files
python3 01_sequential_swarm.py
```

The listing is the run: one subject goes through generation and formatting, and a second is halted when QA rejects the draft. The harness asserts both branches, because the halt is the lesson.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | which branches were exercised |

## Notes

- The handoff is a Pydantic object, not a string: each role receives a schema and returns the next one.
- The mock model is keyed on the schema name it is asked for, which is why the two agents never see each other's prompt.
- The halt path is a second class of outcome, not an exception: the orchestrator stops and says why.
