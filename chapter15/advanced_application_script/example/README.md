# Example 2 — the self-debugging agent

## What it does

The full loop: a scripted model writes a median function with no input validation, the tests fail, the failure is packaged as JSON for the refiner, and the corrected code passes on the second cycle.

## The listings

| file | what it is |
| --- | --- |
| `01_refinement_agent.py` | the listing: the test wrapper, the sandbox, the refinement loop |
| `run_refinement_agent.py` | the harness: runs the loop in `output/` and checks both cycles |

## Run it

```bash
cd chapter15/advanced_application_script/example/files
python3 01_refinement_agent.py
```

The listing is the run: cycle 1 fails on the missing validation, the refiner payload is printed, and cycle 2 passes. The harness asserts both cycles and exits non-zero if the sandbox feedback stops being parsed.

## What it produces

Written by the harness (and by the listing itself, which leaves it behind):

| path | what it is |
| --- | --- |
| `output/agent_sandbox/` | the generated `solution.py` and `run_tests.py` |
| `output/result.json` | the number of cycles |

## Notes

- The first failure is an assertion — `ValueError not raised` — not a `TypeError`: a list of strings sorts fine, so the function quietly returns the middle element.
- The test wrapper redirects both `stdout` and `stderr`; `unittest` reports to stderr, so capturing only stdout made every run look like `UNKNOWN_ERROR`.
- The wrapper also needs `import json` for its own `json.dumps(feedback)`; without it the parent never saw the contract and fell back to `EXECUTION_ERROR`.
