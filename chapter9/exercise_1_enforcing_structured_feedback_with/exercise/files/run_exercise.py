"""Harness for exercise 1: Pydantic-style validation."""
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
    h = Harness("exercise 1 (validators)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_pydantic_validators.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "SUCCESS", "the valid payload is accepted")
    h.contains(printed, "out of range", "an out-of-range score is rejected")
    h.contains(printed, "Missing mandatory field", "a missing field is rejected by the validator")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (validators)", FILES).crash())
