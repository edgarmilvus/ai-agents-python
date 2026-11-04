"""Harness for the basic manager-worker simulation."""
import asyncio
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

DURATIONS = [3.5, 1.0, 2.0, 1.5]


def main():
    h = Harness("example 1 (manager-worker)", FILES)
    module = load_listing(FILES / "01_manager_worker_simulation.py", "basic_mas")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        asyncio.run(module.main())
    printed = log.getvalue()

    for task_id in (101, 102, 103, 104):
        h.contains(printed, f"Task {task_id} completed", f"task {task_id} finished")
    h.contains(printed, "SYSTEM STATS", "the run reports the wall-clock total")
    h.equal(printed.count("completed successfully"), 4, "all four tasks completed once")
    h.check(sum(DURATIONS) > max(DURATIONS), "the tasks differ in duration, so the test can tell")
    h.contains(printed, f"{max(DURATIONS):.2f}", "the total runtime is the longest task, not the sum")
    h.check("8.00" not in printed, "the run did not wait for the tasks in sequence")

    h.write_json("result.json", {"tasks": 4, "wall_clock": max(DURATIONS), "serial": sum(DURATIONS)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (manager-worker)", FILES).crash())
