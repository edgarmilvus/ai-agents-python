# Exercise 2 — specialized workers

## What it does

Two specialized workers share one async API client: a data fetcher and an analysis worker, both using `async with` against the same resource.

## The listings

| file | what it is |
| --- | --- |
| `01_async_api_skeleton.py` | the API skeleton from the exercise |
| `02_specialized_workers.py` | the solution: workers, manager and the shared client |
| `run_specialized_workers.py` | the harness: checks the results and the clean close |

## Run it

```bash
cd chapter6/exercise_2_specialized_workers_and_asynchrono/exercise/files
python3 02_specialized_workers.py
```

The listing is the run: it prints the workers' results and the shared resource closing. `run_specialized_workers.py` asserts both and exits non-zero if a worker's result is missing; `01_async_api_skeleton.py` is the API skeleton from the exercise.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of collected results |

## Notes

- Standard library only, no network.
- The workers were constructed with `id=`, but the class takes `agent_id=`; the listing now matches its own constructor.
