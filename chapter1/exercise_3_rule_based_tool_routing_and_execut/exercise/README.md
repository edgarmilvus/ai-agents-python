# Exercise 3 — rule-based tool routing and execution

## What it does

The Act phase of an agent, without an LLM. A query is routed by keyword to one of three mock tools, the tool's arguments are extracted from the query, and the tool is called dynamically through a manifest.

## The listings

| file | what it is |
| --- | --- |
| `01_rule_based_tool_router.py` | the solution: three tools, a manifest, a router and an executor |
| `run_tool_router.py` | the harness: five queries, including one that must not route |

## Run it

```bash
cd chapter1/exercise_3_rule_based_tool_routing_and_execut/exercise/files
python3 01_rule_based_tool_router.py
```

The listing is the run: it routes four queries and prints each tool's answer, including one that no tool handles. The harness adds a fifth query and exits non-zero if a query routes wrongly or the calculator accepts a non-arithmetic string.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/responses.json` | the final response for each of the five queries |

## Notes

- No dependencies beyond the standard library, no network.
- `financial_calculator` still uses `eval`, behind a check that admits only digits, operators, spaces and parentheses.
- The router returns `(None, None)` for an unknown query instead of guessing a tool.
