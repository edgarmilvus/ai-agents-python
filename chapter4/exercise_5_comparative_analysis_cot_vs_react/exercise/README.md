# Exercise 5 — CoT against ReAct

## What it does

The same question answered twice: a CoT answer from stale weights, and a ReAct answer that observes current data before answering. The listing prints both and the comparison.

## The listings

| file | what it is |
| --- | --- |
| `01_cot_vs_react.py` | the solution: both simulated agents and the analysis |
| `run_cot_vs_react.py` | the harness: checks the corrected answer and the reasoning |

## Run it

```bash
cd chapter4/exercise_5_comparative_analysis_cot_vs_react/exercise/files
python3 01_cot_vs_react.py
```

The listing is the run: it prints both agents' answers and the comparison. `run_cot_vs_react.py` asserts the corrected answer and exits non-zero if the observation step is not credited.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the candidates and the answer the ReAct agent reached |

## Notes

- No dependencies beyond the standard library, no network.
- Both agents are simulated: the exercise is the comparison, not the models.
