# Example 3 — the BrowserTool wrapper

## What it does

The DRY wrapper the exercises build on: one class maps string strategies to `By`, waits for visibility before every find, logs and re-raises, and returns a compact page summary instead of the whole DOM.

## The listings

| file | what it is |
| --- | --- |
| `01_browser_tool.py` | the listing: the `BrowserTool` class and its two demo stubs |
| `run_browser_tool.py` | the harness: drives the class against a scripted driver |

## Run it

```bash
cd chapter14/python_implementation_structure/example/files
python3 run_browser_tool.py
```

`01_browser_tool.py` only defines the class; its calls are commented out, so running it prints nothing. The harness drives navigate, type, click and the page summary for real, then walks both failure paths.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the page summary the wrapper returned |

## Notes

- `demonstrate_tool_use` prints the commands an LLM would emit; it does not execute them, which is why the harness drives the class directly.
- A missing element surfaces as `TimeoutException` from the wait, not `NoSuchElementException`: that is what the listing's `except TimeoutException` branch is for.
