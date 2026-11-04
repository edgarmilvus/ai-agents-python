# Exercise 4 — the deployment analyst

## What it does

Two tools with different time horizons: a live service-status lookup and a historical log analyser that counts errors and quotes the last critical one.

## The listings

| file | what it is |
| --- | --- |
| `01_deployment_analyst_agent.py` | the solution from the chapter |
| `run_deployment_analyst.py` | the harness: composes the mock services with this listing and calls the tool |

## Run it

```bash
cd chapter3/exercise_4_interactive_challenge_the_multi_mo/exercise/files
python3 run_deployment_analyst.py
```

`01_deployment_analyst_agent.py` defines the live-status and log tools. `run_deployment_analyst.py` checks both and exits non-zero if a degraded service reads as OK.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the service statuses and the log report |

## Notes

- Runs offline and deterministically; no key is read.
- Needs `sqlalchemy` only where the mock services are composed in.
