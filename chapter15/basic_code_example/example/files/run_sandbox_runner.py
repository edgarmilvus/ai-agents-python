"""Harness for the basic sandbox runner.

The listing's demo runs three snippets through the sandbox, one of them a syntax
error on purpose. The harness runs the file itself and checks that each case lands
in the branch it was written for.
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
    h = Harness("example 1 (sandbox runner)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_sandbox_runner.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "--- Running SUCCESS_CODE", "the success case ran")
    h.contains(printed, "The square of 11 is: 121", "the snippet's output came back through the pipe")
    h.contains(printed, "--- Running RUNTIME_ERROR_CODE", "the runtime case ran")
    h.contains(printed, "ZeroDivisionError", "the traceback was captured as stderr")
    h.contains(printed, "--- Running SYNTAX_ERROR_CODE", "the syntax case ran")
    h.contains(printed, "SyntaxError", "the interpreter's early failure was captured")
    h.equal(printed.count("Exit Code: 0"), 1, "exactly one case exits cleanly")
    h.equal(printed.count("Exit Code: 1"), 2, "the two failures return one")

    h.write_json("result.json", {"cases": 3})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (sandbox runner)", FILES).crash())
