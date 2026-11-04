"""Harness for exercise 1: the LLM rewrites its own locator after a failure."""
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
    h = Harness("exercise 1 (dynamic locator)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_dynamic_locator.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Agent Attempt 1", "the first locator was tried")
    h.contains(printed, "page re-rendered", "the first attempt failed and said why")
    h.contains(printed, "Use CSS_SELECTOR", "the retry switched strategy")
    h.contains(printed, "worked on attempt 2", "the second locator succeeded")
    h.check("maximum retries" not in printed, "the loop did not run out of attempts")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (dynamic locator)", FILES).crash())
