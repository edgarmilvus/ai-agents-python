# Example 3 — the solution shell

## What it does

The skeleton the five exercises extend: the project state, the state hub, the base agent, the role router, the QA agent, the security auditor and the supervisor, with the driver commented out.

## The listings

| file | what it is |
| --- | --- |
| `01_swarm_shell.py` | the listing: every class the exercises use |
| `run_swarm_shell.py` | the harness: exercises the hub and names the roles |

## Run it

```bash
cd chapter20/worked_example_solution_shell_and_setup/example/files
python3 run_swarm_shell.py
```

`01_swarm_shell.py` is a skeleton: its driver is commented out and its monitoring loop never ends, so running it directly prints nothing. The harness imports it and exercises the state hub, the roles and the supervisor directly.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the roles it found |

## Notes

- `SwarmStateHub.wait_for_status` parks a future per target status and wakes it on the transition; that is the mechanism every exercise reuses.
- The shell's `main()` ends in an endless monitoring loop, which is why the harness does not call it.
- `ProjectState.copy` was deprecated in Pydantic 2; the hub uses `model_copy`.
