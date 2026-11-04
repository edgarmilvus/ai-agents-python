# Example 3 — the solution structure

## What it does

The skeleton the four exercises are built on: a state enum, two custom exceptions,
and one class per exercise. It is a structure, not a demo — the classes are defined
and every driver call at the bottom is commented out, which is why the file prints
almost nothing when you run it.

## The listings

| file | what it is |
| --- | --- |
| `01_solution_structure.py` | the listing: the four agent classes |
| `run_solution_structure.py` | the harness: drives two of them and names the rest |

## Run it

```bash
cd chapter13/comprehensive_solution_structure/example/files
python3 run_solution_structure.py
```

`01_solution_structure.py` only defines the four agents, so running it prints
nothing but the constructor line. `run_solution_structure.py` drives the
configuration agent and the risk gate, checks that the gate shows the agent's
state and its recent history, and exits non-zero if the gate stops appearing.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the four agent classes it found |

## Notes

- Standard library only, offline.
- The exercise 3 risk score is now deterministic: an irreversible write scores 9
  and heavy compute scores 6. With `random.randint(1, 10)` the gate fired on
  roughly a third of the runs and the exercise's whole point could go unseen.
