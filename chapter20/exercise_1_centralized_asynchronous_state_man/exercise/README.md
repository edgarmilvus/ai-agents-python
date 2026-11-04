# Exercise 1 — the state hub

## What it does

One state object, one lock, and a future per waiting status. The product owner moves the project to development and then to a QA failure; the developer is parked on each transition and wakes with the artifact in hand.

## The listings

| file | what it is |
| --- | --- |
| `01_state_hub.py` | the solution from the chapter |
| `run_exercise.py` | the harness: loads the sections it depends on, then runs it |

## Run it

```bash
cd chapter20/exercise_1_centralized_asynchronous_state_man/exercise/files
python3 run_exercise.py
```

`01_state_hub.py` is one section of the capstone: it runs on the shared boilerplate, which the harness loads first, exactly as the Solutions section reads. It then checks the two handoffs the demo performs.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The version number increments on every update, so a waiter can tell how far the project has moved.
- The demo's second transition carries a bug count, which is what the developer's fix cycle reads.
- This file is one section of the capstone; the shared boilerplate lives in its own folder.
