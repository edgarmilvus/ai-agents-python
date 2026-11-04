# Exercise 4 — the configuration tool

## What it does

A custom tool with a Pydantic input schema: it reads one key from one section of an INI file, and the agent uses it before advising on a logging level change.

## The listings

| file | what it is |
| --- | --- |
| `01_hint.py` | the tool skeleton from the exercise |
| `02_exercise_4_custom_tool_agent.py` | the working tool, the role and the simulated run |
| `run_config_tool.py` | the harness: the tool's answers and the recommendation |

## Run it

```bash
cd chapter5/exercise_4_the_custom_configuration_tool_agen/exercise/files
python3 02_exercise_4_custom_tool_agent.py
```

The listing is the run: it builds a config file, reads it through the custom tool and prints the recommendation. `run_config_tool.py` checks the tool and the advice, and exits non-zero if the current level or the recommendation drifts; `01_hint.py` is the tool skeleton from the exercise.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the recommendation |

## Notes

- Needs `pydantic` and the standard library; runs offline.
- The tool reports a missing section or key instead of raising.
