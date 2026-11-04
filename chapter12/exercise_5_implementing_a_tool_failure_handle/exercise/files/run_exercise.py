"""Harness for exercise 5: the handler registry."""
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
    h = Harness("exercise 5 (error registry)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        runpy.run_path(str(FILES / "01_error_registry.py"), run_name="__main__")
    printed = log.getvalue()

    h.contains(printed, "Network failure detected", "the network failure is registered")
    h.contains(printed, "Database failure detected", "the database failure is registered")
    h.contains(printed, "RECOVERY_ACTION", "a handler produced a recovery action")
    h.contains(printed, "executed successfully", "a healthy tool still runs")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (error registry)", FILES).crash())
