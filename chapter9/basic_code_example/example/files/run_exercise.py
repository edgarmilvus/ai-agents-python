"""Harness for the structured-critique example."""
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
    h = Harness("example 1 (structured critique)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_structured_critique.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Gamma", "every agent produced a critique")
    h.contains(printed, "Validation Failures", "the invalid critique is reported")
    h.contains(printed, "out of range", "the reason is a range violation")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (structured critique)", FILES).crash())
