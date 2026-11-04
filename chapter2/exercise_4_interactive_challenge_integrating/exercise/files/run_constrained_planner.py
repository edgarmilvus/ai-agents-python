"""Harness for exercise 4: a plan that breaks its own constraint and is rewritten.

The constraint is checked by a tool, not by the prompt, so the harness asserts the
observable sequence: count above the limit, violation, revised plan.
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
    h = Harness("exercise 4 (constrained planning)", FILES)
    ns, printed = compose(FILES / "01_constrained_planner.py")

    h.contains(printed, "Plan complexity count is 5", "the counter measured the first plan")
    h.contains(printed, "CONSTRAINT VIOLATION", "the agent noticed the limit was broken")
    h.contains(printed, "Thought 2", "the agent entered a reflection step")
    h.contains(ns["final_plan"], "Revised Final Plan", "the returned plan is the revised one")
    steps = [line.strip() for line in ns["final_plan"].splitlines()
             if line.strip()[:2] in {"1.", "2.", "3.", "4.", "5."}]
    h.equal(len(steps), 3, "the revised plan has three steps, inside the limit")
    h.equal(ns["step_counter"].name, "PlanStepCounter", "the constraint tool is the one used")
    h.check(ns["final_plan"] != "", "the agent returned a plan, not an error string")

    h.write_json("result.json", {
        "final_plan": ns["final_plan"],
        "violation_detected": "CONSTRAINT VIOLATION" in printed,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (constrained planning)", FILES).crash())
