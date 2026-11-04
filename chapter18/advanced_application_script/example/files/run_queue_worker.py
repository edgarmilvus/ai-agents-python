"""Harness for the RQ-backed API.

The listing needs a Redis server: `Queue(...)` and `enqueue()` talk to it. The
harness replaces the queue with an in-memory one that keeps the same surface —
`enqueue` returns a job with an id, `fetch_job` returns it — so the endpoints, the
models and the status branches are the listing's own.
"""
import importlib.util
import json
import pathlib
import sys
import warnings
from datetime import datetime

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

warnings.simplefilter("ignore")

import redis  # noqa: E402
import rq  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class FakeJob:
    def __init__(self, job_id):
        self.id = job_id
        self.status = "queued"
        self.result = None
        self.exc_info = None
        self.ended_at = datetime(2026, 10, 28, 12, 0, 0)

    def get_status(self):
        return self.status


class FakeQueue:
    """The three attributes the listing uses: enqueue, fetch_job, and the jobs."""

    def __init__(self):
        self.jobs = {}

    def enqueue(self, func, *args, **kwargs):
        job = FakeJob(f"job-{len(self.jobs) + 1}")
        self.jobs[job.id] = job
        return job

    def fetch_job(self, job_id):
        return self.jobs.get(job_id)


def main():
    h = Harness("example 2 (queue worker)", FILES)
    queue = FakeQueue()
    rq.Queue = lambda name, connection=None: queue
    redis.Redis = lambda **kwargs: object()

    spec = importlib.util.spec_from_file_location("queue_worker", str(FILES / "01_queue_worker.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)

    submitted = client.post("/analyze/submit", json={"company_name": "Acme Corp"})
    h.equal(submitted.status_code, 202, "submission is accepted, not completed")
    h.check("status" not in submitted.json(), "the response carries a job id, not a result")
    job_id = submitted.json()["job_id"]
    h.contains(submitted.json()["status_endpoint"], job_id, "the caller is told where to poll")

    # A queued job is not finished yet.
    queued = client.get(f"/analyze/status/{job_id}")
    h.equal(queued.json()["status"], "queued", "the first poll reports the queue")

    # The worker finishes it.
    job = queue.jobs[job_id]
    job.status = "finished"
    job.result = json.dumps({"company": "Acme Corp", "final_sentiment": "Highly Positive"})
    done = client.get(f"/analyze/status/{job_id}")
    h.equal(done.json()["status"], "finished", "the second poll reports completion")
    h.equal(done.json()["result"]["final_sentiment"], "Highly Positive",
            "the stored JSON was deserialised")
    h.contains(done.json()["completion_time"], "2026-10-28", "the completion time is the job's")

    # A failed job exposes the tail of its traceback.
    job.status = "failed"
    job.exc_info = "line1\nline2\nValueError: boom"
    failed = client.get(f"/analyze/status/{job_id}")
    h.equal(failed.json()["status"], "failed", "the failure is reported")
    h.contains(failed.json()["exc_info"], "ValueError: boom", "the traceback tail is returned")

    unknown = client.get("/analyze/status/does-not-exist")
    h.equal(unknown.status_code, 404, "an unknown job is a 404")

    h.write_json("result.json", {"jobs": len(queue.jobs)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (queue worker)", FILES).crash())
