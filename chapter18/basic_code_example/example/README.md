# Example 1 — the FastAPI wrapper

## What it does

One app with two endpoints that exist to be compared: a synchronous ticker check that answers at once, and an asynchronous task that waits five seconds without blocking the event loop.

## The listings

| file | what it is |
| --- | --- |
| `01_fastapi_wrapper.py` | the listing: the app, both endpoints, the server block |
| `run_fastapi_wrapper.py` | the harness: drives the app with `TestClient` |

## Run it

```bash
cd chapter18/basic_code_example/example/files
python3 run_fastapi_wrapper.py
```

`01_fastapi_wrapper.py` starts a real server only under `__main__`. The harness imports the app and drives it with `TestClient`: the quick endpoint, the slow one, and the 405 that shows the second one is POST-only.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the routes the app registered |

## Notes

- The server banner used to print a URL to open in a browser for a POST endpoint; a browser sends GET, so the reader got 405. It now prints the `curl` line.
- `TestClient` runs the app on the same event loop rules as uvicorn, so the async endpoint's five-second wait is visible as wall-clock time.
- The quick endpoint returns in milliseconds and says so in `execution_time_ms`.
