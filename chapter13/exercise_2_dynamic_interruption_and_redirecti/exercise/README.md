# Exercise 2 — interruption and redirection

## What it does

A migration queue that stops when a task is flagged for review and lets the operator pause, skip or replace the remaining work.

## The listings

| file | what it is |
| --- | --- |
| `01_interruption_agent.py` | the solution from the chapter |
| `run_interruption.py` | the harness: pauses at the flag and checks the queue drains |

## Run it

```bash
cd chapter13/exercise_2_dynamic_interruption_and_redirecti/exercise/files
python3 run_interruption.py
```
