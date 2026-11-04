# Example 2 — the state machine gate

## What it does

A single agent written as an explicit state machine. `ANALYZING` produces a
Pydantic proposal, `AWAITING_APPROVAL` runs the gate, and the human's answer picks
the next state: approve moves to `EXECUTING_CRITICAL`, reject moves to
`RETHINKING`, and the workflow ends in `COMPLETED` either way. `E` at the gate is
the communication pattern — the agent explains itself and asks again.

## The listings

| file | what it is |
| --- | --- |
| `01_state_machine_gate.py` | the listing: enums, proposal, tools, agent, two runs |
| `run_state_machine.py` | the harness: plays the operator in both runs |

## Run it

```bash
cd chapter13/advanced_application_script/example/files
python3 01_state_machine_gate.py
```

The listing runs the agent twice and waits for a typed answer each time: `A` for
the first run, `R` for the second. `run_state_machine.py` plays the operator —
`E` then `A` in the first run, `R` in the second — and asserts that the first run
executes the change and the second one does not.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the final state of each run |

## Notes

- Standard library plus `pydantic`; offline.
- The two runs share one goal on purpose: the difference between them is only the
  human's answer, which is what the state machine is for.
- The harness patches `time.sleep`, so the two simulated tool calls do not add
  six seconds to the suite.
