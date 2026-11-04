# Example 3 — the reference shells

## What it does

All four exercises in one script, with a `main()` that runs them in order: the async token budget, context trimming, the caching wrapper and the structured-output comparison.

## The listings

| file | what it is |
| --- | --- |
| `01_solution_shells.py` | the listing: the four exercises and the driver |
| `run_solution_shells.py` | the harness: checks each conclusion |

## Run it

```bash
cd chapter19/worked_example_solution_shells_for_reference/example/files
python3 01_solution_shells.py
```

The listing is the run: it executes all four exercises in sequence and prints their numbers. The harness checks each conclusion, including the trimming goal and the cache hits.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the trimming percentage it measured |

## Notes

- The trimming kept two supporting documents and asserted a 60% reduction it did not reach (51%). It keeps one now, which is what the exercise asks for.
- The expensive tool used `hash(ticker)`, which is salted per process: the printed results changed on every run. It now derives the value from the characters.
