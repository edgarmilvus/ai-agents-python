# Example 3 — the persistence pipeline

## What it does

The exercise pipeline assembled: a pickled config, an async SQLite history writer and an agent that reloads both before its first interaction.

## The listings

| file | what it is |
| --- | --- |
| `01_persistence_pipeline.py` | the listing: the pipeline and two sessions |
| `run_persistence_pipeline.py` | the harness: checks the files and the counters |

## Run it

```bash
cd chapter10/python_code_implementation_block/example/files
python3 01_persistence_pipeline.py
```

The listing is the run: it prints the restored config, the counters and the interaction. `run_persistence_pipeline.py` asserts the files and the counters, and exits non-zero if the pickled state is not reloaded.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/agent_config.pkl` | the pickled configuration |
| `output/agent_history.db` | the SQLite history |
| `output/result.json` | the printed length |

## Notes

- Standard library only, offline.
- The async writer runs its SQLite calls through `asyncio.to_thread`.
