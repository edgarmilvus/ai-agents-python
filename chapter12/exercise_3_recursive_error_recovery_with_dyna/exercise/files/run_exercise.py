"""Harness for exercise 3: recursive recovery."""
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
    h = Harness("exercise 3 (recursive recovery)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_recursive_recovery.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Attempt 1/3", "the first attempt ran")
    h.contains(printed, "CORRECTION NEEDED", "the failure triggered a correction")
    h.contains(printed, "Task completed on attempt 2", "the corrected code passes")
    h.check("FATAL ERROR" not in printed, "the loop does not exhaust its attempts")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (recursive recovery)", FILES).crash())
