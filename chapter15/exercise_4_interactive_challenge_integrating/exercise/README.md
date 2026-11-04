# Exercise 4 — static analysis before execution

## What it does

A style check runs before the sandbox: a PEP 8 violation sends a `STYLE_ERROR` payload straight back to the generator and skips execution entirely. Only clean code reaches the tests.

## The listings

| file | what it is |
| --- | --- |
| `01_static_analysis.py` | the solution from the chapter |
| `run_exercise.py` | the harness: drives the solution and checks the outcome |

## Run it

```bash
cd chapter15/exercise_4_interactive_challenge_integrating/exercise/files
python3 run_exercise.py
```

`01_static_analysis.py` defines the validator and the extended loop. The harness checks the style rules directly, then drives three attempts: style failure, execution failure, success.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The check is deliberately narrow — CamelCase functions and mixedCase variables — because it stands in for a linter, not for one.
- A style failure costs no subprocess: the whole point of validating first.
- Standard library plus `pydantic`; offline. The sketch printed in the exercise text is book-only because it assumes the classes from the exercise above.
