# Exercise 2 — the financial analyst

## What it does

A price lookup over the mock API. It upper-cases the ticker, formats the timestamp and turns an unknown ticker into an error message rather than a guess.

## The listings

| file | what it is |
| --- | --- |
| `01_financial_analyst_agent.py` | the solution from the chapter |
| `run_financial_analyst.py` | the harness: composes the mock services with this listing and calls the tool |

## Run it

```bash
cd chapter3/exercise_2_the_real_time_financial_analyst_ag/exercise/files
python3 run_financial_analyst.py
```

`01_financial_analyst_agent.py` defines the price tool, which needs the mock API. `run_financial_analyst.py` pairs the two and exits non-zero if an unknown ticker is answered instead of reported.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the quoted price and the unknown-ticker answer |

## Notes

- Runs offline and deterministically; no key is read.
- Needs `sqlalchemy` only where the mock services are composed in.
