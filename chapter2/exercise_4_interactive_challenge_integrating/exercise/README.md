# Exercise 4 — constrained planning

## What it does

A planner under a hard limit of four steps. A tool counts the steps of its own plan, the agent notices the violation and rewrites the plan shorter before returning it.

## The listings

| file | what it is |
| --- | --- |
| `01_constrained_planner.py` | the solution from the chapter |
| `run_constrained_planner.py` | the harness: composes the boilerplate with this listing and asserts the result |

## Run it

```bash
cd chapter2/exercise_4_interactive_challenge_integrating/exercise/files
python3 run_constrained_planner.py
```

`01_constrained_planner.py` assumes the chapter's boilerplate, so the harness composes the two published blocks and runs the result. It writes `output/result.json` and exits non-zero if the violation is not detected or the revised plan still breaks the limit.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the revised plan and whether the violation was detected |

## Notes

- Runs offline and deterministically: the boilerplate's `MockLLM` answers, no key is read.
- The harness runs the two published blocks exactly as the book publishes them; neither file is copied or edited.
