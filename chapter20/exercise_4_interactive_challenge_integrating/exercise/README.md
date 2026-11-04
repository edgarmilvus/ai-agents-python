# Exercise 4 — the security auditor

## What it does

A fourth role inserted before QA: the auditor reads the artifact, returns a `SecurityViolation` when it finds one, and the orchestrator routes either kind of report back to the same developer.

## The listings

| file | what it is |
| --- | --- |
| `01_security_auditor.py` | the solution from the chapter |
| `run_exercise.py` | the harness: loads the sections it depends on, then runs it |

## Run it

```bash
cd chapter20/exercise_4_interactive_challenge_integrating/exercise/files
python3 run_exercise.py
```

`01_security_auditor.py` is one section of the capstone: it needs the boilerplate, the developer from exercise 2 and the QA agent from exercise 3, and the harness loads all three first.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- The loop handles two report types with the same branch: `BugReport` and `SecurityViolation` both carry a remediation instruction.
- The delivered artifact is printed with its final version, which is what the two iterations changed.
- This file is one section of the capstone; the shared boilerplate lives in its own folder.
