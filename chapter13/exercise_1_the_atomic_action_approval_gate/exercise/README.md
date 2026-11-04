# Exercise 1 — the atomic action approval gate

## What it does

A configuration agent that cannot apply an irreversible change without an approval recorded in its own state machine.

## The listings

| file | what it is |
| --- | --- |
| `01_atomic_approval_agent.py` | the solution from the chapter |
| `run_atomic_approval.py` | the harness: answers the gate and checks the applied change |

## Run it

```bash
cd chapter13/exercise_1_the_atomic_action_approval_gate/exercise/files
python3 run_atomic_approval.py
```
