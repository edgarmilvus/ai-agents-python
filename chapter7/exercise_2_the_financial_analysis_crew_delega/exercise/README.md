# Exercise 2 — the financial crew

## What it does

Delegation with a structured result: a quantitative analyst who can delegate, and a report whose expected output is a JSON object.

## The listings

| file | what it is |
| --- | --- |
| `01_financial_crew.py` | the solution from the chapter |
| `run_crew.py` | the harness: scripted model, the crew's output |

## Run it

```bash
cd chapter7/exercise_2_the_financial_analysis_crew_delega/exercise/files
python3 run_crew.py
```

`01_financial_crew.py` needs a key and a provider, so the harness scripts the model and runs the crew. It exits non-zero if the risk report stops being produced.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model calls and the printed length |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The solution had no imports of its own (it assumed the setup block); it now imports what it uses.
