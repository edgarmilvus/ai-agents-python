# Exercise 4 — dynamic scaling

## What it does

A pool that grows under a burst and shrinks when idle: a queue, workers with an idle timeout, and a monitor that hires, retires, and keeps a minimum.

## The listings

| file | what it is |
| --- | --- |
| `01_worker_pool_skeleton.py` | the worker-pool skeleton from the exercise |
| `02_dynamic_scaling.py` | the solution: worker, manager, monitor and the scenario |
| `run_dynamic_scaling.py` | the harness: runs the scenario under a timeout |

## Run it

```bash
cd chapter6/exercise_4_interactive_challenge_dynamic_work/exercise/files
python3 02_dynamic_scaling.py
```

The listing is the run: it prints hires, retirements and the final shutdown. `run_dynamic_scaling.py` runs it under a timeout and exits non-zero if the pool deadlocks; `01_worker_pool_skeleton.py` is the skeleton from the exercise.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | whether the run finished, plus the hire and retirement counts |

## Notes

- Standard library only; the scenario takes about 40 seconds because the waits are real.
- The original monitor only retired workers while the pool was above its floor, so the last worker died and the second burst waited forever; the harness's timeout is what catches that.
