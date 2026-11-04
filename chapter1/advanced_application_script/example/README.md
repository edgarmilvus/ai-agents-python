# Example 2 — the self-correcting validation agent

## What it does

A goal with a hard constraint instead of a research question. The agent validates a project proposal against length rules, reads the failure report, produces a corrected proposal, and validates again until the status is `GOAL_MET` or the iteration limit is reached.

## The listings

| file | what it is |
| --- | --- |
| `01_self_correcting_validation_agent.py` | the listing: two `@tool` capabilities and a state machine that drives them |
| `run_validation_agent.py` | the harness: runs the agent, then re-checks the rules independently |

## Run it

```bash
cd chapter1/advanced_application_script/example/files
python3 01_self_correcting_validation_agent.py
```

The listing is the run: it prints the OODA trace and the final proposal. The harness asserts the same path and exits non-zero if the agent does not reach `GOAL_MET` in three iterations.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/final_state.json` | the status, the three actions in order, the first error report and the corrected proposal |

## Notes

- Needs `pydantic` and `langchain-core` from `requirements.txt`.
- `@tool` returns a `StructuredTool`, not a function: the loop calls `.invoke({"proposal": ...})`. Calling it directly raises `TypeError: 'StructuredTool' object is not callable` on langchain-core 1.x.
- Deterministic: no randomness and no network.
