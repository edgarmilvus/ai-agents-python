"""Harness for the reflection loop around a tool."""
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
    h = Harness("example 2 (reflection loop)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_reflection_loop.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "FAILURE DETECTED", "the first attempt failed")
    h.contains(printed, "Correction Applied", "the reflection proposed a new input")
    h.contains(printed, "SUCCESS", "the retry succeeded")
    h.contains(printed, "GOOGL", "the corrected input reached the tool")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (reflection loop)", FILES).crash())
