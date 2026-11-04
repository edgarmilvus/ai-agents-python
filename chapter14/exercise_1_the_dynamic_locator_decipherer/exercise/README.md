# Exercise 1 — the dynamic locator

## What it does

A locator agent that reads a DOM snippet, asks the model for a strategy and a value, tries it, and — when the page has re-rendered — feeds the failure back and lets the model choose a class-based selector instead.

## The listings

| file | what it is |
| --- | --- |
| `01_dynamic_locator.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter14/exercise_1_the_dynamic_locator_decipherer/exercise/files
python3 01_dynamic_locator.py
```

The listing is the run: the first locator fails on the re-rendered page and the rewrite succeeds on the second attempt. `run_exercise.py` asserts both attempts, the strategy change and the success, and exits non-zero if the retry stops happening.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Attempt 1 used to succeed, so the retry branch — the whole point of the exercise — was unreachable. The mock now fails the first attempt with the reason the prompt needs.
- Standard library only, offline: every Selenium call in the listing is a mock.
