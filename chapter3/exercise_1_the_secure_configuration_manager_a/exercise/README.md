# Exercise 1 — the secure configuration manager

## What it does

Two file tools: one reads a JSON configuration, the other updates a single key without dropping the rest. Missing and corrupt files are reported as strings the model can act on.

## The listings

| file | what it is |
| --- | --- |
| `01_secure_config_agent.py` | the solution from the chapter |
| `run_secure_config.py` | the harness: composes the mock services with this listing and calls the tool |

## Run it

```bash
cd chapter3/exercise_1_the_secure_configuration_manager_a/exercise/files
python3 run_secure_config.py
```

`01_secure_config_agent.py` defines the two file tools and runs nothing. `run_secure_config.py` calls them against a temporary config and exits non-zero if an error is swallowed or a key is lost.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the configuration after the updates |

## Notes

- Runs offline and deterministically; no key is read.
- Needs `sqlalchemy` only where the mock services are composed in.
