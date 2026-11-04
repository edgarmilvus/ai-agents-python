# Exercise 3 — the QA loop

## What it does

QA as a role: it tests the artifact, returns a structured `BugReport` when it fails, and the orchestrator routes that report back to the developer until the artifact passes.

## The listings

| file | what it is |
| --- | --- |
| `01_qa_loop.py` | the solution from the chapter |
| `run_exercise.py` | the harness: loads the sections it depends on, then runs it |

## Run it

```bash
cd chapter20/exercise_3_formalizing_the_qa_and_iterative_r/exercise/files
python3 run_exercise.py
```

`01_qa_loop.py` is one section of the capstone: it needs the boilerplate and the developer from exercise 2, and the harness loads both first. It checks that the first artifact fails QA and the refined one passes.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The QA verdict used to be `random.random() < 0.6`, so the demo sometimes passed immediately and lost the loop; it now fails the first artifact and passes the second.
- The bug report carries steps to reproduce and a suggested fix, which is what the developer's refinement prompt receives.
- This file is one section of the capstone; the shared boilerplate lives in its own folder.
