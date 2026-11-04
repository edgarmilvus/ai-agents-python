# Exercise 2 — structured output with a cutoff

## What it does

A research task whose output is a Pydantic model: query, cutoff date, summary, source count and insights. The prompt carries the date and the schema validates the result.

## The listings

| file | what it is |
| --- | --- |
| `01_example_python_setup_snippet_ill.py` | the schema snippet the exercise starts from |
| `02_exercise_2_dynamic_structured_agent.py` | the working version: prompt, mock call and validation |
| `run_dynamic_agent.py` | the harness: validates the report and the schema's refusals |

## Run it

```bash
cd chapter5/exercise_2_dynamic_goal_setting_and_structure/exercise/files
python3 02_exercise_2_dynamic_structured_agent.py
```

The listing is the run: it produces and validates the structured report. `run_dynamic_agent.py` checks the schema and exits non-zero if the cutoff date or an insight is lost; `01_example_python_setup_snippet_ill.py` is the schema it grew from.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the validated report |

## Notes

- Needs `pydantic`; runs offline.
- The schema rejects a non-numeric source count, which the harness checks.
