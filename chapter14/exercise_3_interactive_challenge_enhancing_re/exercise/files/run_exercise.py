"""Harness for exercise 3: visual verification with a confidence threshold."""
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
    h = Harness("exercise 3 (visual verification)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_visual_verification.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.equal(printed.count("--- Starting Verification for Goal:"), 2,
            "both scenarios ran")
    h.contains(printed, "QA Result | Success: True | Confidence: 0.99",
               "the matching order was confirmed")
    h.contains(printed, "QA Result | Success: False | Confidence: 0.35",
               "the mismatch was caught")
    h.contains(printed, "ACTION REQUIRED", "the low score triggered recovery")
    h.equal(printed.count("Verification passed"), 1,
            "only the matching order passed")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (visual verification)", FILES).crash())
