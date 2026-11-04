# Example 1 — the manager and the workers

## What it does

Four simulated tasks, one manager and asyncio: the manager starts a coroutine per task and gathers the results, so the wall-clock time is the longest task rather than the sum.

## The listings

| file | what it is |
| --- | --- |
| `01_manager_worker_simulation.py` | the listing: worker coroutine, manager and the gathered run |
| `run_basic_mas.py` | the harness: checks the total and that nothing ran in sequence |

## Run it

```bash
cd chapter6/basic_code_example/example/files
python3 01_manager_worker_simulation.py
```

The listing is the run: it prints four workers finishing in the time of the longest task. `run_basic_mas.py` asserts the same total and exits non-zero if the tasks start running in sequence.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the task count, the wall-clock total and the serial sum |

## Notes

- Standard library only, no network.
- The durations are fixed, so the arithmetic in the log is checkable.
