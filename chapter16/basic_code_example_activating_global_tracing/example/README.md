# Example 1 — global tracing

## What it does

One LCEL chain — prompt, model, parser — under a block of environment variables. Nothing in the chain knows about LangSmith: the switch is `LANGCHAIN_TRACING_V2`, and the project name decides where the run lands.

## The listings

| file | what it is |
| --- | --- |
| `01_global_tracing.py` | the listing: key setup, the chain, one invocation |
| `run_global_tracing.py` | the harness: tracing off, a fake model, the same chain |

## Run it

```bash
cd chapter16/basic_code_example_activating_global_tracing/example/files
python3 run_global_tracing.py
```

`01_global_tracing.py` calls a real model and, when a LangSmith key is present, sends the trace to the service. The harness supplies a fake model, turns the switch off and checks that the chain still answers: tracing is an observer, and its absence must not change the result.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | whether tracing was on |

## Notes

- The listing used to prompt for `OPENAI_API_KEY` and hardcode `gpt-3.5-turbo`; it now reads `OPENAI_COMPATIBLE_*` like the rest of the volume.
- The switch is set with `setdefault`, so an environment that says `false` wins. Forcing it to `true` makes the listing untestable without an account.
- The banner prints what the variable actually says, not what the listing wished for.
