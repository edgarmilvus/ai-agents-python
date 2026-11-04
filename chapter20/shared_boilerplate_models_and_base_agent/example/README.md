# Example 4 — the shared boilerplate

## What it does

The vocabulary of the capstone: `ProjectState`, `BugReport`, `SecurityViolation` and `BaseAgent`, with its queue, its two submission paths and its health check.

## The listings

| file | what it is |
| --- | --- |
| `01_swarm_boilerplate.py` | the listing: three models and the base agent |
| `run_swarm_boilerplate.py` | the harness: checks the contracts |

## Run it

```bash
cd chapter20/shared_boilerplate_models_and_base_agent/example/files
python3 run_swarm_boilerplate.py
```

`01_swarm_boilerplate.py` only defines the models and the base agent. The harness checks their contracts: the state defaults, the id ranges, and the two ways to submit work — the future, and the result.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the agent it exercised |

## Notes

- `submit_task` returns a future; `run_task` awaits it. The exercises used to `await submit_task(...)` and then index the future, which is what `Future object is not subscriptable` meant.
- The health check raises `ConnectionError` after two seconds when an agent is marked unresponsive — that is what the supervisor watches for.
