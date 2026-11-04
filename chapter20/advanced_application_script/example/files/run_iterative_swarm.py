"""Harness for the iterative swarm.

The loop is the point: the mocked QA must fail the first draft and pass the refined
one, so the trace shows a real refinement rather than three identical attempts.
"""
import contextlib
import io
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 2 (iterative swarm)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_iterative_swarm.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "[PO] Analyzing high-level goal", "the product owner ran first")
    h.contains(printed, "Defined Requirements:", "the requirements were structured")
    h.contains(printed, "--- ITERATION 1 ---", "the first iteration ran")
    h.contains(printed, "FAILURE detected", "the first draft was rejected")
    h.contains(printed, "test': 'input 5', 'passed': False", "the failure names the failing case")
    h.contains(printed, "--- ITERATION 2 ---", "the loop ran a second time")
    h.contains(printed, "Refining code based on QA feedback", "the feedback reached the developer")
    h.contains(printed, "SUCCESS! QA passed the code", "the refined draft passed")
    h.contains(printed, "Optimized iterative implementation after bug fix",
               "the final deliverable is the refined code")
    h.check("Failed to reach consensus" not in printed, "the loop did not exhaust its attempts")

    h.write_json("result.json", {"iterations": 2})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (iterative swarm)", FILES).crash())
