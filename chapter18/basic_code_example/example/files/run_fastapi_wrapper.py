"""Harness for the FastAPI wrapper.

The listing starts a server only under `__main__`, so the harness imports the app
and drives it with `TestClient`: the quick synchronous endpoint, the slow one, and
the method guard that makes the second one POST-only.
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


def main():
    h = Harness("example 1 (fastapi wrapper)", FILES)
    spec = importlib.util.spec_from_file_location("fastapi_wrapper", str(FILES / "01_fastapi_wrapper.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)

    quick = client.get("/quick_check/MSFT")
    h.equal(quick.status_code, 200, "the sync endpoint answers")
    h.equal(quick.json()["status"], "ok", "the sync response carries a status")
    h.contains(quick.json()["message"], "MSFT", "the ticker came back in the message")
    h.equal(quick.json()["task_type"], "quick_sync", "the sync response names its task type")

    missing = client.get("/quick_check/")
    h.equal(missing.status_code, 404, "a missing path parameter does not match the route")

    slow = client.post("/run_complex_agent/", params={"ticker": "GOOG"})
    h.equal(slow.status_code, 200, "the async endpoint answers")
    h.equal(slow.json()["task_type"], "long_async", "the async response names its task type")
    h.contains(slow.json()["result"], "GOOG", "the ticker reached the long task")

    wrong_verb = client.get("/run_complex_agent/", params={"ticker": "GOOG"})
    h.equal(wrong_verb.status_code, 405, "the async endpoint is POST-only")

    h.write_json("result.json", {"routes": [route.path for route in module.app.routes if hasattr(route, "path")]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (fastapi wrapper)", FILES).crash())
