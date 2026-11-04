# Exercise 5 — the self-healing swarm

## What it does

A supervisor that polls its agents' health, notices a hung developer, provisions a replacement and hands it the failed agent's queue.

## The listings

| file | what it is |
| --- | --- |
| `01_self_healing.py` | the solution from the chapter |
| `run_exercise.py` | the harness: loads the sections it depends on, then runs it |

## Run it

```bash
cd chapter20/exercise_5_building_the_self_healing_swarm_re/exercise/files
python3 run_exercise.py
```

`01_self_healing.py` is one section of the capstone: it needs the boilerplate and the agents from exercises 2 and 3. The harness loads them, then watches the supervisor detect a hung agent and replace it.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The recovery is a new agent object, not a retry on the old one: the supervisor rebuilds it and re-registers it.
- The task submitted after recovery really completes, which is the check that the replacement is wired to a working loop.
- This file is one section of the capstone; the shared boilerplate lives in its own folder.
