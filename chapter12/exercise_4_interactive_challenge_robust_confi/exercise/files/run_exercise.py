"""Harness for exercise 4: startup configuration."""
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
    h = Harness("exercise 4 (robust configuration)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "02_robust_config.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Generated Usage Guide", "the LLM produced a usage guide")
    h.contains(printed, "STARTUP SUCCESS", "a valid argument list starts the agent")
    h.contains(printed, "FLASH", "a missing argument is reported")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (robust configuration)", FILES).crash())
