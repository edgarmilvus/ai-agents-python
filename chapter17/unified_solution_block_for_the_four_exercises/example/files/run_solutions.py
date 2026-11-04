"""Harness for the unified solutions.

The block runs all four solutions at import. The harness checks the four
conclusions, plus the guardrail's three classifications, which are what make the
RAG agent safe rather than merely polite.
"""
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
    h = Harness("example 4 (unified solutions)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_solutions.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    # --- exercise 1
    h.contains(printed, "--- Exercise 1: Multi-Layered Input Sanitization Pipeline ---",
               "the pipeline demo ran")
    h.contains(printed, "FAILED (Expected Blacklist)", "the blacklist case is blocked")
    h.contains(printed, "FAILED (Expected Pattern)", "the pattern case is blocked")
    h.contains(printed, "FAILED (Expected Length)", "the length case is blocked")

    # --- exercise 2
    h.contains(printed, "PASS: Valid call to search_database", "the valid call passes")
    h.contains(printed, "FAIL (Expected Whitelist)", "the unknown tool is rejected")
    h.contains(printed, "FAIL (Expected Schema)", "the malformed call is rejected")

    # --- exercise 3
    h.contains(printed, "Task completed successfully in", "the short task fits its budget")
    h.contains(printed, "Execution budget of 1.00s exceeded", "the overrun is reported")
    h.contains(printed, "Task 2: Operation finished. (The budget is only checked on exit.)",
               "the cooperative limit is stated")

    # --- exercise 4
    h.contains(printed, "[Guardrail] Classification: SAFE", "the safe query passed the guardrail")
    h.contains(printed, "[Guardrail] Classification: UNSAFE", "the injection was classified unsafe")
    h.contains(printed, "[Guardrail] Classification: OFF_TOPIC", "the joke was classified off-topic")
    h.contains(printed, "SECURITY ALERT: Malicious intent detected", "the unsafe query was blocked")
    h.contains(printed, "RAG Result: Successfully generated", "the safe query reached retrieval")

    h.write_json("result.json", {"exercises": 4})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (unified solutions)", FILES).crash())
