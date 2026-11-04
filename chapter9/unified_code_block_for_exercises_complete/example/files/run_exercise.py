"""Harness for the complete exercise block."""
import contextlib
import io
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 4 (exercise complete)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_exercise_complete.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "records persisted", "the mock database commits")
    h.contains(printed, "Total records in simulated DB: 3", "three critiques are stored")
    h.contains(printed, "Refinements", "the stored refinements are read back")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (exercise complete)", FILES).crash())
