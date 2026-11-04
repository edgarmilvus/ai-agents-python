"""Harness for the shared framework of the five exercises."""
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
    h = Harness("example 3 (exercise framework)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_exercise_framework.py"), run_name="__main__")
    printed = log.getvalue()

    for number in (1, 2, 4, 5):
        h.contains(printed, f"exercise {number}", f"exercise {number} ran")
    h.contains(printed, "[VALIDATION SUCCESS]", "the validator accepted a valid payload")
    h.contains(printed, "[HANDLER LOG]", "the error registry handled a failure")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise framework)", FILES).crash())
