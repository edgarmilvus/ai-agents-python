# Exercise 3 — recursive recovery

## What it does

A generator, a reviewer and a recursive retry: the review's feedback becomes the next prompt, and the second attempt passes.

## The listings

| file | what it is |
| --- | --- |
| `01_recursive_recovery.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the outcome |

## Run it

```bash
cd chapter12/exercise_3_recursive_error_recovery_with_dyna/exercise/files
python3 01_recursive_recovery.py
```

The listing is the run: it fails, reflects and passes on the second attempt. `run_exercise.py` asserts the success and exits non-zero if the loop exhausts its attempts.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the printed length of the run |

## Notes

- Standard library only, offline.
- The reviewer prompt contains the constraint, which names the forbidden syntax; the check now looks only at the code section, so a compliant rewrite passes.
