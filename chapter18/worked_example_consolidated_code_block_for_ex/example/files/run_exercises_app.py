"""Harness for the consolidated exercise app.

The block simulates RQ in-process, so the harness can drive it end to end: the
synchronous endpoint, its validation, a job submission, the polling endpoint with
and without long polling, and the dynamic tool registry.
"""
import importlib.util
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

warnings.simplefilter("ignore")

from fastapi.testclient import TestClient  # noqa: E402

QUERY = "Summarize the quarterly revenue for the board"


def main():
    h = Harness("example 3 (exercises app)", FILES)
    spec = importlib.util.spec_from_file_location("exercises_app", str(FILES / "01_exercises_app.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)

    sync = client.post("/agent/execute_sync", json={"query": QUERY, "context_id": "session-1"})
    h.equal(sync.status_code, 200, "the sync endpoint answers")
    h.equal(sync.json()["status"], "completed", "the sync response is completed")
    h.contains(sync.json()["result"], QUERY, "the query came back")

    too_short = client.post("/agent/execute_sync", json={"query": "hi", "context_id": "session-1"})
    h.equal(too_short.status_code, 422, "a query below the minimum length is rejected")

    submitted = client.post("/agent/submit", json={
        "query": QUERY, "context_id": "session-1", "required_tools": ["math_solver"]})
    h.equal(submitted.status_code, 200, "the job was accepted")
    h.equal(submitted.json()["status"], "submitted", "submission returns immediately")
    job_id = submitted.json()["job_id"]

    queued = client.get(f"/agent/status/{job_id}")
    h.check(queued.json()["status"] in {"queued", "started", "finished"},
            "the queued job has a state")

    done = client.get(f"/agent/status/{job_id}", params={"long_poll": "true"})
    h.equal(done.status_code, 200, "long polling returned before the timeout")
    h.equal(done.json()["status"], "finished", "the worker finished the job")
    h.contains(done.json()["result"], "Math Solver executed", "the registered tool ran")
    h.contains(done.json()["result"], "session-1", "the context id survived the queue")

    unknown = client.get("/agent/status/not-a-job")
    h.equal(unknown.status_code, 404, "an unknown job is a 404")

    unknown_tool = client.post("/agent/submit", json={
        "query": QUERY, "context_id": "session-2", "required_tools": ["no_such_tool"]})
    result = client.get(f"/agent/status/{unknown_tool.json()['job_id']}",
                        params={"long_poll": "true"}).json()["result"]
    h.contains(result, "not found in registry", "an unknown tool is reported, not raised")

    h.write_json("result.json", {"routes": [route.path for route in module.app.routes if hasattr(route, "path")]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercises app)", FILES).crash())
