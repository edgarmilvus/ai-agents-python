# Exercise 1 — simulating the OODA loop

## What it does

A resource collector agent. Each turn it observes the environment, orients the observation against the goal of 10 units, decides whether to collect or terminate, and acts on that decision. The loop stops only when the Act phase carries out a `Terminate` decision.

## The listings

| file | what it is |
| --- | --- |
| `01_ooda_resource_collector.py` | the solution: four phases as four functions over one `world_state` |
| `run_ooda_collector.py` | the harness: seeds the environment, checks the phase order and the ending |

## Run it

```bash
cd chapter1/exercise_1_simulating_the_ooda_loop/exercise/files
python3 01_ooda_resource_collector.py
```

The listing is the run: it prints the four phases of one episode. The harness seeds the generator, asserts the same episode and exits non-zero if the phases run out of order or the loop does not end on a termination act.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed, the observation of every iteration, the total collected and the iteration count |

## Notes

- `random` is seeded by the harness (seed 7), so the numbers in `output/result.json` are reproducible.
- Running the listing directly uses the unseeded generator: the numbers change, the shape does not.
- The terminating pass still observes; that observation is never collected.
