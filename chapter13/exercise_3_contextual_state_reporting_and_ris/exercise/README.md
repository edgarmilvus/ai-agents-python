# Exercise 3 — risk-aware contextual approval

## What it does

An analysis agent that scores each task, shows the operator the recent history, and gates only the action that cannot be undone.

## The listings

| file | what it is |
| --- | --- |
| `01_risk_reporting_agent.py` | the solution from the chapter |
| `run_risk_reporting.py` | the harness: approves the one gate and counts it |

## Run it

```bash
cd chapter13/exercise_3_contextual_state_reporting_and_ris/exercise/files
python3 run_risk_reporting.py
```
