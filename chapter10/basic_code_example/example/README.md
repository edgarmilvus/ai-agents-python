# Example 1 — the state snapshot

## What it does

One agent state serialised with `pickle` between runs: the session counter and the history log survive a restart, and the second run continues from the first.

## The listings

| file | what it is |
| --- | --- |
| `01_state_snapshot.py` | the listing: load, run a session, save |
| `run_state_snapshot.py` | the harness: runs it twice and compares the state |

## Run it

```bash
cd chapter10/basic_code_example/example/files
python3 01_state_snapshot.py
```

The listing is the run: it prints the restored session count and the reloaded history. `run_state_snapshot.py` runs it twice and exits non-zero if the second run starts from an empty state.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/agent_state.pkl` | the pickled state |
| `output/result.json` | the snapshot size |

## Notes

- Standard library only, offline.
- The listing is designed to be run twice; the harness does exactly that and asserts the counter.
