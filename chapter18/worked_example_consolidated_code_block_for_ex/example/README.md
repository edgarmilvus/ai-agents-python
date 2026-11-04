# Example 3 — the exercise app

## What it does

One FastAPI app carrying the four exercises: a validated synchronous endpoint, a submission endpoint, a status endpoint with optional long polling, and a worker that activates only the tools the caller lists.

## The listings

| file | what it is |
| --- | --- |
| `01_exercises_app.py` | the listing: models, tool registry, simulated queue, endpoints |
| `run_exercises_app.py` | the harness: drives all four through `TestClient` |

## Run it

```bash
cd chapter18/worked_example_consolidated_code_block_for_ex/example/files
python3 run_exercises_app.py
```

The listing is a runnable app: `python3 01_exercises_app.py` serves it under uvicorn. The harness drives the same app through `TestClient` — synchronous call, validation, submission, long polling and the dynamic tool registry — so the suite needs no port and no worker.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the routes the app registered |

## Notes

- The simulated worker used `asyncio.create_task`, whose task dies with the request that started it; under uvicorn it survived, under any test client it never ran. It is a thread now, which is closer to a separate worker process.
- The job's simulated duration was `random.randint(10, 15)` seconds; it is now 1–3, so the polling demo is watchable.
- An unknown tool key is reported inside the job result instead of raising in the worker.
