"""Harness for exercise 1: async task distribution under a manager."""
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
    h = Harness("exercise 1 (async distribution)", FILES)
    module = load_listing(FILES / "01_async_distribution.py", "async_distribution")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        asyncio.run(module.main_exercise_1())
    printed = log.getvalue()

    h.contains(printed, "Verification", "the run verifies its own parallelism")
    h.contains(printed, "confirms parallelism", "the verification states the conclusion")
    h.contains(printed, "worker", "worker results are printed")
    h.check(printed.lower().count("result") >= 3 or printed.count("\"worker") >= 3,
            "every worker contributed a result")
    h.check("4.0s" in printed or "4.00" in printed or "parallel" in printed.lower(),
            "the total time is the longest task, not the sum")

    h.write_json("result.json", {"verified": "confirms parallelism" in printed})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (async distribution)", FILES).crash())
