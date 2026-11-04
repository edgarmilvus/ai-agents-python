# Example 4 — the solution template

## What it does

All four exercises in one file, each as a function: sequential content, delegation with structured output, a hierarchical launch crew and a validation gate.

## The listings

| file | what it is |
| --- | --- |
| `01_solution_template.py` | the template: four crews and their entry points |
| `run_solution_template.py` | the harness: runs all four against a scripted model |

## Run it

```bash
cd chapter7/solution_template_and_code_structure/example/files
python3 run_solution_template.py
```

`01_solution_template.py` needs a key and a provider, so the harness scripts the model and runs all four crews. It writes `output/result.json` and exits non-zero if any exercise stops producing a result.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of exercises and model calls |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The hierarchical crew names its manager in `manager_agent` only; CrewAI 1.x rejects a manager that is also listed in `agents`.
- Live, exercise 3 is the fragile one: a reasoning model can keep re-reading the
  manager's deferred tool results and trip CrewAI's repeated-call guard, or run for
  many minutes. Exercises 1, 2 and 4 pass against the real API; the hierarchical
  one is why `run_live.sh` keeps it behind `--slow`.
