# Example 3 — the scaling template

## What it does

The reference implementation of the dynamic worker pool: a queue, workers that idle out, and a monitor that hires under load and retires idle capacity while keeping a floor.

## The listings

| file | what it is |
| --- | --- |
| `01_scaling_template.py` | the listing: worker, pool manager, monitor and the scenario |
| `run_scaling_template.py` | the harness: runs the scenario under a timeout and checks the phases |

## Run it

```bash
cd chapter6/python_implementation_template_for_reference/example/files
python3 01_scaling_template.py
```

The listing is the run: it prints a burst, the scaling decisions and the shutdown. `run_scaling_template.py` runs the same scenario under a timeout and exits non-zero if the queue never drains.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | whether the scenario finished inside the timeout |

## Notes

- Standard library only; the scenario takes about 40 seconds because the waits are real.
- A worker that idles out must be retired and replaced even at the pool floor: otherwise the last worker dies silently and the next burst is never served.
