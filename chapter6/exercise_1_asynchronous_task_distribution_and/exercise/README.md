# Exercise 1 — async task distribution

## What it does

A manager distributes four tasks to worker coroutines and collates the results, with a timing check that proves the tasks overlapped.

## The listings

| file | what it is |
| --- | --- |
| `01_async_distribution.py` | the solution: workers, distribution and the verification |
| `run_async_distribution.py` | the harness: checks the parallelism claim |

## Run it

```bash
cd chapter6/exercise_1_asynchronous_task_distribution_and/exercise/files
python3 01_async_distribution.py
```

The listing is the run: it prints the workers' results and the parallelism check. `run_async_distribution.py` asserts that check and exits non-zero if the total stops being the longest task.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | whether the parallelism check passed |

## Notes

- Standard library only, no network.
- The durations are fixed so the comparison is meaningful.
