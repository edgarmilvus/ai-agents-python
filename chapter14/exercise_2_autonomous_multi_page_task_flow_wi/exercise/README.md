# Exercise 2 — multi-page memory

## What it does

A three-page flow driven by a planner that reads memory: log in, select the Pro tier, confirm the order. Memory carries the goal, the credentials and the page reached so far.

## The listings

| file | what it is |
| --- | --- |
| `01_multi_page_memory.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter14/exercise_2_autonomous_multi_page_task_flow_wi/exercise/files
python3 01_multi_page_memory.py
```

The listing is the run: login, tier selection, confirmation, success. `run_exercise.py` checks each page in turn and exits non-zero if the run stalls.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The reset at the start of the run rebuilt the driver but not the tool that holds it, so the agent read the login page forever and never left step 3. Both are rebound now, and the run ends on the success page.
- Standard library only, offline: every Selenium call in the listing is a mock.
