# Example 4 — the exercise tools

## What it does

The seven tools the exercises start from: config read and update, a stock lookup, an ORM query, a service-status check, a log analyser and a validated hash.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_tools.py` | the starter tools, with their validation and error messages |
| `run_exercise_tools.py` | the harness: composes the tools with the mock services and calls each one |

## Run it

```bash
cd chapter3/starter_code_for_the_exercises/example/files
python3 run_exercise_tools.py
```

`01_exercise_tools.py` defines seven tools and runs nothing. `run_exercise_tools.py` composes it with the mock services, calls each tool and exits non-zero if one of their contracts breaks.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/starter.json` | the digest, the filtered inventory and the log report |

## Notes

- Needs `sqlalchemy` (through the mock services); runs offline.
- The harness composes the two published blocks instead of copying either of them.
