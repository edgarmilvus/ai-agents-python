"""Harness for exercise 1: the asynchronous token budget."""
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
    h = Harness("exercise 1 (async budget)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_async_budget.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Token Budget Manager (Success Case)", "the success case ran")
    h.contains(printed, "[SUCCESS] Context finished. Final token usage: 75 (Budget: 100)",
               "the run stayed inside its budget")
    h.contains(printed, "Budget breach detected", "the long run was stopped")
    h.contains(printed, "Caught expected error:", "the breach was caught by the caller")
    h.check("This line should not be reached" not in printed,
            "the call after the breach never ran")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (async budget)", FILES).crash())
