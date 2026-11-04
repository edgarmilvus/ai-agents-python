# Example 1 — the digital librarian

## What it does

A plain Selenium script, no LLM: start headless Chrome, open Wikipedia, find the search box by its id, type a query, press ENTER, read the resulting title and close the session. Every step is commented with what the WebDriver is doing.

## The listings

| file | what it is |
| --- | --- |
| `01_digital_librarian.py` | the listing: driver setup, navigation, one search |
| `run_browser_flow.py` | the harness: a scripted driver that records the flow |

## Run it

```bash
cd chapter14/basic_code_example/example/files
python3 run_browser_flow.py
```

`01_digital_librarian.py` drives a real Chrome against Wikipedia, so the fence above runs the harness instead: it installs the scripted driver from `tools/fake_selenium.py` and checks that the query reached the search box, that ENTER submitted it, and that the session was closed.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the urls visited and the text typed |

## Notes

- The listing wraps everything in `try/except`, so a broken flow still exits 0 with an `[ERROR]` line; the harness is what turns that into a failure.
- Run it for real with `pip install -r requirements-browser.txt` and Chrome
installed; the target is `https://www.wikipedia.org/`, so it needs the network
too. The advanced listing points at a placeholder job board and cannot run.
- The script sleeps three seconds after ENTER. That is the pitfall the next section is about.
