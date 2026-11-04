# Example 3 — the exercise boilerplate

## What it does

The shared scaffold the four exercise solutions assume: a scripted LLM, a vector store, an abstract tool, a stock lookup, a moving average, a stateful shopping cart and a step counter. It defines behaviour and runs nothing.

## The listings

| file | what it is |
| --- | --- |
| `01_boilerplate_code_for_exercises.py` | the library the four solutions import by composition |
| `run_boilerplate.py` | the harness: instantiates each mock and checks the behaviour the exercises rely on |

## Run it

```bash
cd chapter2/boilerplate_code_for_exercises/example/files
python3 run_boilerplate.py
```

The harness instantiates every mock `01_boilerplate_code_for_exercises.py` defines. It writes `output/boilerplate.json` and exits non-zero if the plan, the retrieval, the cart or the step counter stops behaving as those solutions assume.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/boilerplate.json` | the classes found, the plan length and the counter's reading |

## Notes

- No network and no key: every collaborator is a mock.
- `ShoppingCartTool.run()` dispatches to `add_item`, `view_cart` and `checkout`; without it the class cannot be instantiated, because `BaseTool.run` is abstract.
