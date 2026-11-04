"""Harness for exercise 2: a Manager plan executed step by step.

The plan is produced by the boilerplate's mock, so what is worth checking is the
orchestration: three steps are parsed, each tool receives the arguments from the
step (including `window`, which sits outside `input`), and the second step's
output is what the synthesis quotes.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

CHAPTER = ROOT / "chapter2"
BOILERPLATE = (CHAPTER / "boilerplate_code_for_exercises/example/files"
               / "01_boilerplate_code_for_exercises.py")


def compose(solution: pathlib.Path):
    source = BOILERPLATE.read_text() + "\n\n" + solution.read_text()
    namespace = {"__name__": "__main__"}
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), namespace)
    return namespace, log.getvalue()


def main():
    h = Harness("exercise 2 (hierarchical planning)", FILES)
    ns, printed = compose(FILES / "01_hierarchical_planner.py")

    h.contains(printed, "Manager Plan Generated (3 steps)", "the manager produced a three-step plan")
    h.contains(printed, "Step 1 Result (Tool: StockPriceLookup)", "step 1 called the price tool")
    h.contains(printed, "Step 2 Result (Tool: CalculateMovingAverage)",
               "step 2 called the average tool")
    h.check("Execution failed" not in printed,
            "no step failed for a missing argument")
    h.contains(ns["final_report"], "50-day moving average",
               "the synthesis quotes the second step's result")
    h.contains(ns["final_report"], "HOLD", "the synthesis ends on a recommendation")
    h.equal(ns["manager_llm"].call_count, 1, "the manager was consulted once")

    h.write_json("result.json", {
        "report": ns["final_report"],
        "manager_calls": ns["manager_llm"].call_count,
        "log": printed.splitlines(),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (hierarchical planning)", FILES).crash())
