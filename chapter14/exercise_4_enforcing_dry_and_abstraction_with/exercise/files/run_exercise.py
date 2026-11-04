"""Harness for exercise 4: one tool method per LLM command, failures included."""
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
    h = Harness("exercise 4 (DRY browser tool)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_browser_tool_dry.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "LLM Generates (High-level, DRY)",
               "the demo states the commands the LLM would emit")
    h.contains(printed, "username_input received 'agent_user'",
               "the typed text reached the element")
    h.contains(printed, "Mock Click: //button", "the submit element was clicked")
    h.contains(printed, "Timeout: Element not visible using ID='fail_id'",
               "a failing locator is logged, not raised")
    h.contains(printed, "Click failed for ID='fail_id'",
               "the wrapper reports the failure to the caller")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (DRY browser tool)", FILES).crash())
