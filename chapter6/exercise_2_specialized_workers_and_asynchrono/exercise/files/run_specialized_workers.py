"""Harness for exercise 2: specialized workers sharing one async resource."""
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
    h = Harness("exercise 2 (specialized workers)", FILES)
    module = load_listing(FILES / "02_specialized_workers.py", "specialized_workers")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        asyncio.run(module.main_exercise_2())
    printed = log.getvalue()

    h.contains(printed, "FINAL RESULTS SUMMARY", "the manager prints one summary")
    h.contains(printed, "Connection safely closed", "the shared async resource is released")
    h.contains(printed, "Real-Time Quote", "the data-fetching worker produced a quote")
    h.contains(printed, "RSI Calculation", "the analysis worker produced a calculation")
    h.check(printed.count("finished:") >= 3, "three worker results are collected")
    h.check(printed.count("$") >= 2, "the mock prices reached the summary")

    h.write_json("result.json", {"results": printed.count("finished:")})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (specialized workers)", FILES).crash())
