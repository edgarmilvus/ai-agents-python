# Exercise 1 — the content crew

## What it does

A sequential two-agent crew: research first, article introduction second, with the first output as the second task's context.

## The listings

| file | what it is |
| --- | --- |
| `01_content_crew.py` | the solution from the chapter |
| `run_crew.py` | the harness: scripted model, the crew's output |

## Run it

```bash
cd chapter7/exercise_1_the_technical_content_writer_crew/exercise/files
python3 run_crew.py
```

`01_content_crew.py` needs a key and a provider, so the harness scripts the model and runs the crew. It exits non-zero if the article result stops being printed.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model calls and the printed length |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
