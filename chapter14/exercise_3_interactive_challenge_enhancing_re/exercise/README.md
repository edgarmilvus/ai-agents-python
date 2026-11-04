# Exercise 3 — visual verification

## What it does

Two orders go through a mocked transaction and a mocked QA analyst: one matches the goal exactly, one confirms a single unit with a red alert. The confidence score decides whether the agent accepts the result or escalates it.

## The listings

| file | what it is |
| --- | --- |
| `01_visual_verification.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter14/exercise_3_interactive_challenge_enhancing_re/exercise/files
python3 01_visual_verification.py
```

The listing is the run: one order verifies at 0.99, the suspicious one at 0.35 and triggers recovery. `run_exercise.py` asserts both and that only one passes.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The scenario was chosen by looking for `purchase 5 units` in the goal, which both goals contain, so the suspicious case produced the success page. It now checks the scenario marker.
- Standard library only, offline: every Selenium call in the listing is a mock.
