"""Harness for the self-debugging agent.

The listing simulates the model: the first code it writes is missing the input
validation the tests demand, and the corrected code is scripted. The harness runs
the whole loop in the project's output folder and checks that the sandbox really
did report the failure and the second cycle really did pass.
"""
import contextlib
import io
import os
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 2 (self-debugging agent)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    stdout, stderr = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            runpy.run_path(str(FILES / "01_refinement_agent.py"), run_name="__main__")
    finally:
        os.chdir(previous)
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "--- CYCLE 1: Testing Generated Code ---", "the first cycle ran")
    h.contains(printed, "Status: FAILURE", "the failing test was reported as a failure")
    h.contains(printed, "test_validation_error", "the report names the test that failed")
    h.contains(printed, "test_feedback", "the refiner received a structured payload")
    h.contains(printed, "--- CYCLE 2: Testing Generated Code ---", "the refined code was tested")
    h.contains(printed, "Status: SUCCESS", "the second cycle passed")
    h.contains(printed, "[SUCCESS]: All tests passed", "the loop stopped on success")
    h.contains(printed, 'raise ValueError("Input must be a list of numbers.")',
               "the final code carries the fix")
    h.check("[ERROR]: Unexpected execution error" not in printed,
            "the sandbox feedback parsed instead of falling back")

    h.write_json("result.json", {"cycles": 2})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (self-debugging agent)", FILES).crash())
