# Exercise 3 — result aggregation

## What it does

Two workers disagree, and the manager resolves the conflict with an explicit rule: a low-reliability source caps the final confidence instead of winning the average.

## The listings

| file | what it is |
| --- | --- |
| `01_result_aggregation.py` | the solution: findings, the rule and two scenarios |
| `run_aggregation.py` | the harness: checks both verdicts and the rule |

## Run it

```bash
cd chapter6/exercise_3_advanced_result_aggregation_and_co/exercise/files
python3 01_result_aggregation.py
```

The listing is the run: it prints both scenarios and the rule that resolved each. `run_aggregation.py` asserts the verdicts and exits non-zero if a scenario stops producing one.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of scenarios that reached a verdict |

## Notes

- Standard library only, no network.
- The rule is data, so a new conflict type is a new entry, not a new branch.
