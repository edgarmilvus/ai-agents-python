"""Harness for exercise 2: login, configuration and confirmation across pages."""
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
    h = Harness("exercise 2 (multi-page memory)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_multi_page_memory.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Step 1: Login Page", "the run starts on the login page")
    h.contains(printed, "Page transition to /config", "the login advanced to the wizard")
    h.contains(printed, "Step 3: Configuration Wizard", "the agent read the new page")
    h.contains(printed, "Text 'Pro' sent to element 'tier_select'",
               "the tier choice reached the wizard")
    h.contains(printed, "Goal achieved", "the flow reached the success page")
    h.check("maximum steps" not in printed, "the run did not stall")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (multi-page memory)", FILES).crash())
