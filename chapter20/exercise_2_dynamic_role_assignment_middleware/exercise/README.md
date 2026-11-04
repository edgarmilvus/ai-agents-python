# Exercise 2 — the role router

## What it does

A middleware that picks the least busy developer for each task and keeps the work off the caller's thread: nine features, three agents, every queue drained.

## The listings

| file | what it is |
| --- | --- |
| `01_role_router.py` | the solution from the chapter |
| `run_exercise.py` | the harness: loads the sections it depends on, then runs it |

## Run it

```bash
cd chapter20/exercise_2_dynamic_role_assignment_middleware/exercise/files
python3 run_exercise.py
```

`01_role_router.py` is one section of the capstone, run here on the shared boilerplate. The harness checks that all nine tasks are routed and that every developer drains its queue.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- `route_task` returns the future rather than awaiting it, which is what lets the caller `gather` all nine at once.
- The workload counter is decremented in `process_tasks`, so "0 tasks remaining" is a real check, not a print.
- This file is one section of the capstone; the shared boilerplate lives in its own folder.
