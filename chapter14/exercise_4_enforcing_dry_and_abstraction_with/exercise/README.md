# Exercise 4 — the DRY browser tool

## What it does

The same wrapper as the structure, with a mock driver: three high-level commands from the planner become three method calls, and the third one targets an element that does not exist to show the centralised error handling.

## The listings

| file | what it is |
| --- | --- |
| `01_browser_tool_dry.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter14/exercise_4_enforcing_dry_and_abstraction_with/exercise/files
python3 01_browser_tool_dry.py
```

The listing is the run: three commands through the wrapper, the last one failing on purpose. `run_exercise.py` asserts the two successes and the logged failure.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The mock waits return the locator as the condition, which is why `until(condition)` indexes into it — a small stub, kept as the exercise wrote it.
- Standard library only, offline: every Selenium call in the listing is a mock.
