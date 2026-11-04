# Example 1 — the tool schema

## What it does

A deterministic function and the schema that describes it to a model. The listing also simulates the dispatch, so the conversion and the schema can be read side by side.

## The listings

| file | what it is |
| --- | --- |
| `01_tool_schema.py` | the listing: function, schema and a simulated call |
| `run_tool_schema.py` | the harness: checks the conversion and that schema and signature agree |

## Run it

```bash
cd chapter3/basic_code_example/example/files
python3 01_tool_schema.py
```

The listing is the run: it converts a value and prints the simulated agent's dispatch. `run_tool_schema.py` asserts the same conversion and exits non-zero if the schema stops naming the argument the function actually takes.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/schema.json` | the schema, the function name and a sample conversion |

## Notes

- No dependencies beyond the standard library, no network.
- The chapter's pitfall lives here: the schema's key must be the argument the function actually takes.
