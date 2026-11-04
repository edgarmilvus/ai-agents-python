"""Harness for the consolidated exercise scripts.

The block runs all four demos at import. The harness checks each one's conclusion,
including the budget's documented limitation: a cooperative context manager
reports an overrun when the block exits, it does not interrupt the block.
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
    h = Harness("example 3 (exercise scripts)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_exercise_scripts.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    # --- exercise 1
    h.contains(printed, "--- Exercise 1 Demonstration ---", "the sanitizer demo ran")
    h.contains(printed, "--- Sanitization successful.", "the benign prompt passed")
    h.contains(printed, "Blacklisted term detected", "the blacklisted prompt was blocked")
    h.contains(printed, "Input too short", "the length floor fired")
    h.contains(printed, "Suspicious repetitive pattern", "the obfuscation pattern fired")

    # --- exercise 2
    h.contains(printed, "PASS: Valid call to search_database", "a whitelisted tool passed")
    h.contains(printed, "not whitelisted for execution", "an unknown tool was rejected")
    h.contains(printed, "Missing required keys", "a malformed call was rejected")

    # --- exercise 3
    h.contains(printed, "Task completed successfully in", "a short task stays inside its budget")
    h.contains(printed, "Execution budget of 1.00s exceeded", "the overrun is reported")
    h.contains(printed, "Task 2: Operation finished. (The budget is only checked on exit.)",
               "the cooperative limit is stated where the reader meets it")

    # --- exercise 4
    h.contains(printed, "[Guardrail] Classification: SAFE", "a technical query is allowed")
    h.contains(printed, "[Guardrail] Classification: UNSAFE", "an injection is refused")
    h.contains(printed, "[Guardrail] Classification: OFF_TOPIC", "an off-topic query is redirected")
    h.contains(printed, "RAG Result: Successfully generated", "the allowed query reached retrieval")

    h.write_json("result.json", {"exercises": 4})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise scripts)", FILES).crash())
