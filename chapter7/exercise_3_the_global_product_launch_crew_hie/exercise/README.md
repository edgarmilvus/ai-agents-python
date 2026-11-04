# Exercise 3 — the launch crew

## What it does

A hierarchical crew: one manager coordinating marketing and legal, with the manager named by `manager_agent`.

## The listings

| file | what it is |
| --- | --- |
| `01_launch_crew.py` | the solution from the chapter |
| `run_crew.py` | the harness: scripted model, the crew's output |

## Run it

```bash
cd chapter7/exercise_3_the_global_product_launch_crew_hie/exercise/files
python3 run_crew.py
```

`01_launch_crew.py` needs a key and a provider, so the harness scripts the model and runs the hierarchical crew. It exits non-zero if the launch strategy stops being produced.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model calls and the printed length |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- CrewAI 1.x rejects a crew that lists its manager among the agents; the listing was fixed to match.
