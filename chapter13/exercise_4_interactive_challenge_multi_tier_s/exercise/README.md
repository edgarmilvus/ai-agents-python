# Exercise 4 — the two-tier secure pipeline

## What it does

A deployment pipeline with two gates of different weight: a plain approval to leave staging, and a question plus a secret before production.

## The listings

| file | what it is |
| --- | --- |
| `01_secure_deployment_agent.py` | the solution from the chapter |
| `run_secure_deployment.py` | the harness: clears both tiers with the authorization code |

## Run it

```bash
cd chapter13/exercise_4_interactive_challenge_multi_tier_s/exercise/files
python3 run_secure_deployment.py
```
