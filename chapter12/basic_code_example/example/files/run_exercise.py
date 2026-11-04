"""Harness for the self-correcting execution architecture."""
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
    h = Harness("example 1 (self-correction)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_self_correcting_architecture.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "[ATTEMPT 1]", "the loop numbers its attempts")
    h.contains(printed, "FAILURE DETECTED", "the first output is rejected")
    h.contains(printed, "self-corrected on attempt 2", "the corrected output is accepted")
    h.check("status" in printed, "a status is reported")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (self-correction)", FILES).crash())
