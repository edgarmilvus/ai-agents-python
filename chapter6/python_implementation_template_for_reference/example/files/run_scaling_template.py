"""Harness for the reference template: dynamic scaling end to end."""
import asyncio
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 3 (scaling template)", FILES)
    module = load_listing(FILES / "01_scaling_template.py", "scaling_template")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        try:
            asyncio.run(asyncio.wait_for(module.main_exercise_4(), timeout=90))
            finished = True
        except asyncio.TimeoutError:
            finished = False
    printed = log.getvalue()

    h.check(finished, "the scenario finishes instead of deadlocking on the queue")
    h.contains(printed, "Starting Exercise 4", "the run announces itself")
    h.contains(printed, "burst", "the burst phase ran")
    h.contains(printed, "reactivate workers", "the second load was submitted")
    h.contains(printed, "Dynamic MAS shutdown complete", "the system shuts down cleanly")
    h.check("Retired Worker" in printed, "at least one worker retired")
    h.check("Hired Worker" in printed, "at least one worker was hired")

    h.write_json("result.json", {"finished": finished})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (scaling template)", FILES).crash())
