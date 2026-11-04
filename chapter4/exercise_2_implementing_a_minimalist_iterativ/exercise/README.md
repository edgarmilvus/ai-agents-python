# Exercise 2 — the minimal ReAct loop

## What it does

A hand-written ReAct loop: the prompt is a string, the tool returns random statuses, and the loop keeps observing until the server is operational with a load under 50%.

## The listings

| file | what it is |
| --- | --- |
| `01_react_starter.py` | the skeleton the exercise starts from |
| `02_react_agent.py` | the working loop, with the import it needs and the stop condition |
| `run_react_loop.py` | the harness: seeds the tool and checks the loop reaches the target |

## Run it

```bash
cd chapter4/exercise_2_implementing_a_minimalist_iterativ/exercise/files
python3 02_react_agent.py
```

The listing is the run: it prints every observation until the target state is reached. `run_react_loop.py` seeds the random tool, checks the loop and exits non-zero if it stops before the load is under 50%; `01_react_starter.py` is the same loop before the fix.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed, the number of observations and whether the target was reached |

## Notes

- No dependencies beyond the standard library; the tool is random, so the harness seeds it.
- The solution needs `import textwrap`, which the starter had and the solution had lost.
