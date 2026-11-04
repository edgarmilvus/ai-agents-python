# Chapter 18 — Deploying Agents: API Wrappers and Asynchronous Queues

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_fastapi_wrapper.py` | one app, one sync endpoint, one async |
| `advanced_application_script/example/` | `01_queue_worker.py` | submit 202, poll the job, read the result |
| `worked_example_consolidated_code_block_for_ex/example/` | `01_exercises_app.py` | the four exercises in one app |
| `unified_solution_block_for_the_four_exercises/example/` | `01_solutions_app.py` | the same app, complete |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter18/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter18/output/run_18.log`. Any harness that fails makes the suite
exit 1. No server is started and no Redis is required: each harness imports the
listing's `app` and drives it with `TestClient`, and the one listing that needs a
queue gets an in-memory one. The suite spends about fifteen seconds asleep, because
two of the listings simulate work.

## What the harnesses caught

- **A browser could not reach the slow endpoint.** The server banner printed
  `http://127.0.0.1:8000/run_complex_agent/?ticker=GOOG` as a URL to try, but the
  route is `@app.post`; a browser sends GET and got 405. The banner now prints the
  `curl` line.
- **The simulated worker never ran.** Both apps simulated RQ with
  `asyncio.create_task`, whose task dies with the request that created it: under
  uvicorn it survived, under a test client the job stayed `queued` forever. A
  thread is closer to "a separate worker process" and survives both.
- **The jobs were too slow to watch.** The simulated agent slept
  `random.randint(10, 15)` seconds; it is now 1–3, so polling and long polling both
  finish while the reader is looking at them.
