"""Harness for exercise 4: dynamic worker scaling under burst load."""
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
    h = Harness("exercise 4 (dynamic scaling)", FILES)
    module = load_listing(FILES / "02_dynamic_scaling.py", "dynamic_scaling")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        try:
            asyncio.run(asyncio.wait_for(module.main_exercise_4(), timeout=90))
            finished = True
        except asyncio.TimeoutError:
            finished = False
    printed = log.getvalue()

    h.check(finished, "the queue drains instead of deadlocking")
    h.contains(printed, "Scale Up Triggered", "burst load triggers a hire")
    h.contains(printed, "Retired Worker", "idle workers are retired")
    h.contains(printed, "Dynamic MAS shutdown complete", "the system shuts down cleanly")
    h.check(printed.count("Hired Worker") >= 2, "the pool grew under load")
    h.check(printed.count("Finished queued task") >= 10, "the burst tasks completed")
    h.contains(printed, "Task_12", "the second load was processed")

    h.write_json("result.json", {
        "finished": finished,
        "hires": printed.count("Hired Worker"),
        "retirements": printed.count("Retired Worker"),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (dynamic scaling)", FILES).crash())
