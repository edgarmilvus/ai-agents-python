# Example 3 — the exercise setup

## What it does

The configuration the four exercises share: imports, the provider defaults and one dict that names the model, the gateway and the key.

## The listings

| file | what it is |
| --- | --- |
| `01_exercise_setup.py` | the setup block: imports and the shared configuration dict |
| `run_exercise_setup.py` | the harness: checks the dict points at the gateway |

## Run it

```bash
cd chapter7/exercise_setup/example/files
python3 run_exercise_setup.py
```

`01_exercise_setup.py` is configuration, not a crew: it builds the settings dict the four exercises share. `run_exercise_setup.py` asserts the gateway, the model and the key wiring, and exits non-zero if a vendor model is hard-coded again.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the model string and the base URL |

## Notes

- No crew and no calls: importing it only builds a dictionary.
- `model` carries the `openai/` prefix, which is what selects the OpenAI-compatible provider.
