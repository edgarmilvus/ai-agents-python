# Example 2 — the reflection loop

## What it does

A tool call fails on an empty ticker, the reflection diagnoses it, and the retry uses the ticker the reflection proposed. The execution trace is what the reflection reads.

## The listings

| file | what it is |
| --- | --- |
| `01_reflection_loop.py` | the listing: tool, reflection prompt, loop and summary |
| `run_exercise.py` | the harness: checks the correction and the success |

## Run it

```bash
cd chapter12/advanced_application_script/example/files
python3 01_reflection_loop.py
```

The listing is the run: it prints the failure, the reflection and the retry that succeeds. `run_exercise.py` asserts the corrected ticker and exits non-zero if the loop aborts.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The reflection mock now matches the error text the tool actually raises (`Ticker cannot be empty`), not a phrase that only the prompt's title used.
