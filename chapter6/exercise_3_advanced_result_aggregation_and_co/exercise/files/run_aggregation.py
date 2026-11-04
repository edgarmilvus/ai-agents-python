"""Harness for exercise 3: aggregating disagreeing worker results."""
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
    h = Harness("exercise 3 (result aggregation)", FILES)
    module = load_listing(FILES / "01_result_aggregation.py", "aggregation")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        asyncio.run(module.main_exercise_3())
    printed = log.getvalue()

    h.contains(printed, "SCENARIO 1", "the first disagreement is resolved")
    h.contains(printed, "SCENARIO 2", "the second disagreement is resolved")
    h.contains(printed, "FINAL SCORE", "each scenario produces a final confidence")
    h.contains(printed, "Synthesis Summary", "the manager explains its decision")
    h.check("Rule" in printed or "rule" in printed, "the resolution names the rule it applied")
    h.check(printed.count("FINAL SCORE") >= 2, "both scenarios reached a verdict")

    h.write_json("result.json", {"scenarios": printed.count("FINAL SCORE")})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (result aggregation)", FILES).crash())
