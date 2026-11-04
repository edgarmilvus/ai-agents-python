# Example 1 — the contextual calculator

## What it does

A ReAct agent with one tool and a short-term memory. It answers a question directly, calls `calculate_square` when a square is asked for, and on the third turn recalls the number it was told to remember before squaring it.

## The listings

| file | what it is |
| --- | --- |
| `01_contextual_calculator.py` | the listing: tool, memory, ReAct prompt and executor |
| `02_tool_description.py` | the docstring snippet from the pitfall: the text a model reads before calling a tool |
| `run_contextual_calculator.py` | the harness: a scripted chat model, three turns, assertions on memory and the tool |
| `run_tool_description.py` | the harness for the snippet: asserts what the description says and what the schema exposes |

## Run it

```bash
cd chapter2/basic_code_example/example/files
python3 run_contextual_calculator.py
```

The harness swaps `ChatOpenAI` for a scripted model and drives the ReAct loop through three turns. It writes `output/trace.json` and exits non-zero if the tool or the memory fails to carry the context; `run_tool_description.py` checks the docstring snippet the same way.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/trace.json` | the three turns, the model used and the memory after the run |
| `output/description.json` | the tool's name, description and argument schema |

## Notes

- Needs `langchain-classic`, `langchain-community` and `langchain-openai` from `requirements.txt`.
- Running a listing that builds a client needs `OPENAI_COMPATIBLE_API_KEY`; the harnesses do not.
- `OPENAI_COMPATIBLE_BASE_URL` defaults to `https://openrouter.ai/api/v1` and `OPENAI_COMPATIBLE_MODEL` to `~deepseek/deepseek-flash-latest`.
- The tool converts `Action Input` with `int()`: ReAct hands it text, and `"7" * "7"` is not 49.
