"""Harness for exercise 2: runtime versus logical failures."""
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
    h = Harness("exercise 2 (failure classification)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_error_classification.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Runtime Failure", "the network error is classified as runtime")
    h.contains(printed, "Logical Failure", "the 404 is classified as logical")
    h.contains(printed, "RETRY_STRATEGY", "the runtime failure gets a retry plan")
    h.contains(printed, "REPLAN_STRATEGY", "the logical failure gets a replan")
    h.contains(printed, "[SUCCESS]", "the valid identifier succeeds")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (failure classification)", FILES).crash())
