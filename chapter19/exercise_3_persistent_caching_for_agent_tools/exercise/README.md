# Exercise 3 — the caching wrapper

## What it does

A callable wrapper keyed on its arguments: the first call runs the expensive tool, the second returns the stored result, and the total time shows the saving.

## The listings

| file | what it is |
| --- | --- |
| `01_persistent_cache.py` | the solution from the chapter |
| `run_exercise.py` | the harness: runs the listing and checks the trace |

## Run it

```bash
cd chapter19/exercise_3_persistent_caching_for_agent_tools/exercise/files
python3 01_persistent_cache.py
```

The listing is the run: two cold calls execute, two repeats come from the cache. The harness asserts two misses, two hits and that each repeat returned the value of its original.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | what the harness measured |

## Notes

- The demo used `hash(ticker)`, salted per process, so the printed results changed between runs; the value now comes from the characters.
- The wrapper serialises `args` and `kwargs` with `json.dumps(..., sort_keys=True)`, which is what makes the key stable.
- Offline: the model calls are simulated or mocked, and `tiktoken` supplies the token counts.
