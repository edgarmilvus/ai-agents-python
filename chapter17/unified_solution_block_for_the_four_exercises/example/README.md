# Example 4 — the four solutions

## What it does

The same four exercises, complete: four sanitizer failures, three tool-call verdicts, a budget overrun and a guardrail that classifies SAFE, UNSAFE and OFF_TOPIC before any retrieval happens.

## The listings

| file | what it is |
| --- | --- |
| `01_solutions.py` | the listing: the four solutions, executed at import |
| `run_solutions.py` | the harness: checks each conclusion |

## Run it

```bash
cd chapter17/unified_solution_block_for_the_four_exercises/example/files
python3 01_solutions.py
```

The listing is the run: the four solutions print their traces. The harness checks the four conclusions and the guardrail's three classifications, which are what make the RAG agent safe rather than merely polite.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of solutions it checked |

## Notes

- Exercise 3 shares the cooperative budget of the worked example, with the same honest label.
- The guardrail runs before the RAG call, so an unsafe or off-topic prompt costs no retrieval — that ordering is the architecture the exercise asks for.
