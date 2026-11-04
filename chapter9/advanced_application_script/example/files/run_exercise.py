"""Harness for the critique-and-refine loop."""
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
    h = Harness("example 2 (critique loop)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_critique_loop.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Consolidated Refinement", "the loop aggregates advice")
    h.contains(printed, "Cycle", "at least one full cycle ran")
    h.contains(printed, "Score", "scores are reported per cycle")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (critique loop)", FILES).crash())
