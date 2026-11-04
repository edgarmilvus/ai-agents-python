# Example 2 — the RQ-backed service

## What it does

The production shape: a submission endpoint that enqueues work and returns 202 with a job id, and a polling endpoint that reports queued, finished or failed. Redis and RQ do the bookkeeping.

## The listings

| file | what it is |
| --- | --- |
| `01_queue_worker.py` | the listing: queue setup, worker, submit and status endpoints |
| `run_queue_worker.py` | the harness: an in-memory queue with the same surface |

## Run it

```bash
cd chapter18/advanced_application_script/example/files
python3 run_queue_worker.py
```

`01_queue_worker.py` needs a Redis server: the queue talks to it on the first submission. The harness replaces the queue with an in-memory one that keeps the same surface, so the endpoints, the models and the status branches are the listing's own.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the jobs the fake queue held |

## Notes

- The worker sleeps eight seconds in two tool calls; a real RQ worker is a separate process, so that wait costs the request nothing.
- A failed job returns the last five lines of its traceback, which is the difference between "something broke" and a fix.
- The harness sets the job's state by hand, because there is no worker to run it.
To see a real queue: `brew install redis`, start `redis-server`, put the listing
on the path as an importable module, and run `rq worker agent_analysis` beside
it; the job then moves queued -> started -> finished on its own. `./run_queue_demo.sh`
does exactly that, from the repository root, and cleans up after itself.
