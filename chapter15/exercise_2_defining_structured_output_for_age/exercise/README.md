# Exercise 2 — the structured output package

## What it does

`CodeBlock` and `SolutionPackage` pin the shape of a model answer, `parse_agent_output` validates a raw JSON string against them, and `prepare_files_for_execution` writes the two snippets to temporary files.

## The listings

| file | what it is |
| --- | --- |
| `01_structured_output.py` | the solution from the chapter |
| `run_exercise.py` | the harness: drives the solution and checks the outcome |

## Run it

```bash
cd chapter15/exercise_2_defining_structured_output_for_age/exercise/files
python3 run_exercise.py
```

`01_structured_output.py` defines the models and the parser without a demo. The harness parses one valid package and rejects both a non-JSON answer and a package missing its test code.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- A bad answer returns `None` rather than raising; the caller decides whether that is fatal.
- The temporary files are named `solution_agent.py` and `test_solution_agent.py` so two agents on one machine do not collide.
- Standard library plus `pydantic`; offline. The sketch printed in the exercise text is book-only because it assumes the classes from the exercise above.
