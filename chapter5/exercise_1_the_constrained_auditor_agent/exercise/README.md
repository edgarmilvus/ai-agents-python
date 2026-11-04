# Exercise 1 — the constrained auditor

## What it does

An agent whose constitution forbids external access. The only tool is an internal file reader, and the run must state that it cannot perform the CVE check while still analysing the snippet.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_1_auditor_agent.py` | the solution: role, constraint prompt and the simulated run |
| `run_auditor.py` | the harness: checks the refusal and the internal analysis |

## Run it

```bash
cd chapter5/exercise_1_the_constrained_auditor_agent/exercise/files
python3 01_exercise_1_auditor_agent.py
```

The listing is the run: it prints the audit report and its constraint statement. `run_auditor.py` asserts the refusal and the internal analysis, and exits non-zero if the auditor stops naming the tool it was denied.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the audit report |

## Notes

- No network and no key: the reasoning is simulated.
- The constraint is in the role text and in the tool list; both are asserted.
