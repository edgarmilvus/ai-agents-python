"""Harness for the complete solution app.

Same three endpoints as the worked example, with the exercise answers filled in:
validation, submission, long polling and the dynamic tool registry. The harness
drives all of them through `TestClient`; the simulated queue runs the worker in a
thread, so the job really does finish after the submission returns.
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

QUERY = "Prepare the compliance summary for the audit"


def main():
    h = Harness("example 4 (solutions app)", FILES)
    spec = importlib.util.spec_from_file_location("solutions_app", str(FILES / "01_solutions_app.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)

    sync = client.post("/agent/execute_sync", json={"query": QUERY, "context_id": "audit-1"})
    h.equal(sync.status_code, 200, "the sync endpoint answers")
    h.equal(sync.json()["status"], "completed", "the sync response is completed")
    h.equal(sync.json()["execution_time_ms"] >= 0, True, "the response reports its duration")

    for bad in ({"query": "hi", "context_id": "audit-1"},
                {"query": QUERY},
                {"query": QUERY, "context_id": "audit-1", "required_tools": "math_solver"}):
        h.equal(client.post("/agent/execute_sync", json=bad).status_code, 422,
                f"invalid payload rejected: {sorted(bad)}")

    submitted = client.post("/agent/submit", json={
        "query": QUERY, "context_id": "audit-1", "required_tools": ["web_search", "math_solver"]})
    h.equal(submitted.status_code, 200, "the job was accepted")
    h.equal(submitted.json()["status"], "submitted", "submission returns immediately")
    job_id = submitted.json()["job_id"]

    done = client.get(f"/agent/status/{job_id}", params={"long_poll": "true"})
    h.equal(done.status_code, 200, "long polling returned before the timeout")
    h.equal(done.json()["status"], "finished", "the worker finished the job")
    h.contains(done.json()["result"], "Web Search executed", "the first registered tool ran")
    h.contains(done.json()["result"], "Math Solver executed", "the second registered tool ran")
    h.contains(done.json()["result"], "Total Time Taken", "the report names its duration")

    plain = client.get(f"/agent/status/{job_id}")
    h.equal(plain.json()["status"], "finished", "a plain poll sees the same finished job")

    unknown = client.get("/agent/status/not-a-job")
    h.equal(unknown.status_code, 404, "an unknown job is a 404")

    h.write_json("result.json", {"result": done.json()["result"]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (solutions app)", FILES).crash())
