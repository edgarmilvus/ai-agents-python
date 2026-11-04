# Example 1 — the sequential crew

## What it does

Two agents and two tasks in sequence: a researcher produces three facts, a writer turns them into a social post, and the second task starts only when the first one's output exists.

## The listings

| file | what it is |
| --- | --- |
| `01_sequential_crew.py` | the listing: two agents, two tasks, one crew |
| `run_basic_crew.py` | the harness: a scripted CrewAI model and the crew's shape |

## Run it

```bash
cd chapter7/basic_code_example/example/files
python3 run_basic_crew.py
```

`01_sequential_crew.py` needs a key and a provider, so the harness scripts CrewAI's model and runs the same crew. It writes `output/result.json` and exits non-zero if the two agents stop being sequential.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the output and the number of model calls |

## Notes

- Needs `crewai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The LLM is explicit (`LLM(model="openai/…", base_url=…, api_key=…)`): with no `llm`, CrewAI falls back to OpenAI's endpoint.
- CrewAI 1.x validates `verbose` as a boolean, so the crew passes `True`, not `2`.
