# Example 4 — the solution app

## What it does

The same app with the answers filled in: three validation failures, a job that runs two registered tools, long polling that returns as soon as the job finishes, and a plain poll that sees the same result.

## The listings

| file | what it is |
| --- | --- |
| `01_solutions_app.py` | the listing: the complete app |
| `run_solutions_app.py` | the harness: drives every endpoint |

## Run it

```bash
cd chapter18/unified_solution_block_for_the_four_exercises/example/files
python3 run_solutions_app.py
```

`01_solutions_app.py` is a runnable app, served with uvicorn like the worked example. The harness drives it through `TestClient`: three invalid payloads, one job with two registered tools, long polling and the 404.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the job result the app produced |

## Notes

- Validation is left to Pydantic: a short query, a missing `context_id` and a string where a list belongs all come back as 422 without an `if` in the endpoint.
- Long polling sleeps with `await asyncio.sleep`, so the event loop serves other requests while it waits — the whole point of the async endpoint.
- The worker thread is the simulated broker: real RQ replaces it without touching the endpoints.
