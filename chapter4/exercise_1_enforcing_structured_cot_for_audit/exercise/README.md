# Exercise 1 — structured CoT

## What it does

A prompt template that fixes the section headers of the answer, so the reasoning can be audited step by step. The execution prints a simulated answer that follows the template exactly.

## The listings

| file | what it is |
| --- | --- |
| `01_structured_cot.py` | the solution: the template and one simulated execution |
| `run_structured_cot.py` | the harness: checks the headers, the recommendation and the score |

## Run it

```bash
cd chapter4/exercise_1_enforcing_structured_cot_for_audit/exercise/files
python3 01_structured_cot.py
```

The listing is the run: it prints the structured answer section by section. `run_structured_cot.py` asserts the same headers and the recommendation, and exits non-zero if the format or the score drifts.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the headers, the recommendation and the score that were asserted |

## Notes

- No dependencies beyond the standard library, no network.
- The answer is simulated: the exercise is about the template, not about a model call.
