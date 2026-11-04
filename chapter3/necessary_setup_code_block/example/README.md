# Example 3 — the mock services

## What it does

The scaffold the five exercises run against: an in-memory SQLAlchemy inventory, a mock financial API, a service-health map, and two mock files (a config and a deployment log) created on import.

## The listings

| file | what it is |
| --- | --- |
| `01_mock_services.py` | the library: models, seeded database, API mock and mock files |
| `run_mock_services.py` | the harness: seeds nothing, reads everything, checks the contracts |

## Run it

```bash
cd chapter3/necessary_setup_code_block/example/files
python3 run_mock_services.py
```

`01_mock_services.py` is a library: it seeds the database and writes its mock files, then stops. `run_mock_services.py` calls the pieces and exits non-zero if the seed, the API or the files stop behaving as the exercises assume.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/mock_services.json` | the inventory size, tickers, service map and file names |
| `output/agent_config.json` | the config file the exercises read and update |
| `output/deployment_logs.txt` | the log file the analyst exercise reads |

## Notes

- Needs `sqlalchemy` from `requirements.txt`; runs offline.
- The block seeds itself at import; the harness only reads, because seeding twice trips the unique constraint on the item name.
- Files are created inside `output/` because the harness changes directory before importing.
