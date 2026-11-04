"""Harness for exercise 1: the format validator."""
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
    h = Harness("exercise 1 (format validator)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_format_validator.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "[VALIDATION SUCCESS]", "the valid payload is accepted")
    h.contains(printed, "Missing required key", "a missing key is named")
    h.contains(printed, "Status code violation", "a bad status is named")
    h.equal(printed.count("[VALIDATION FAILURE]"), 2, "both failures are rejected")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (format validator)", FILES).crash())
