# Exercise 4 — the validation gate

## What it does

A validation gate between creation and scheduling: the content is checked before the deployment plan is produced.

## The listings

| file | what it is |
| --- | --- |
| `01_validation_crew.py` | the solution from the chapter |
| `run_crew.py` | the harness: scripted model, the crew's output |

## Run it

```bash
cd chapter7/exercise_4_interactive_challenge_integrating/exercise/files
python3 run_crew.py
```

`01_validation_crew.py` needs a key and a provider, so the harness scripts the model and runs the crew. It exits non-zero if the validated content stops being produced.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model calls and the printed length |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The `__main__` block used to call the other three exercises, which this file does not define.
