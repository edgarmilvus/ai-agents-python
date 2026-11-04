"""Harness for exercise 3: contextual state reporting and risk assessment.

The gate has to be the exception, not the rule, so the harness counts the
approvals and checks that the irreversible write is the one that asks."""
import builtins
import contextlib
import io
import pathlib
import sys
import time

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

BOILERPLATE = (ROOT / "chapter13" / "shared_boilerplate_for_the_solutions"
               / "example" / "files" / "01_shared_solution_boilerplate.py")
SOLUTION = FILES / "01_risk_reporting_agent.py"


def answer(message: str) -> str:
    """One scripted operator: approve, resume, grant the code, keep moving."""
    text = str(message)
    if "Authorization Code" in text:
        return "PROD_OVERSEER_2024"
    if "new comma-separated" in text:
        return "fileA,fileB"
    if "(P/S/R)" in text:
        return "P"
    if "Y/N" in text:
        return "Y"
    return ""


def compose():
    """The book publishes this listing against the shared block, so prepend it."""
    source = BOILERPLATE.read_text() + "\n\n" + SOLUTION.read_text()
    namespace = {"__name__": "__main__"}
    log = io.StringIO()
    real_input, real_sleep = builtins.input, time.sleep
    builtins.input = lambda message="": answer(message)
    time.sleep = lambda *_: None
    try:
        with contextlib.redirect_stdout(log):
            exec(compile(source, str(SOLUTION), "exec"), namespace)
    finally:
        builtins.input, real_sleep = real_input, real_sleep
        time.sleep = real_sleep
    return namespace, log.getvalue()


def main():
    h = Harness("exercise 3 (risk-aware reporting)", FILES)
    ns, printed = compose()
    h.contains(printed, "Calculated risk for", "the agent scores each task before running it")
    h.contains(printed, "HUMAN INTERVENTION REQUIRED", "the high-risk write pauses")
    h.contains(printed, "Risk acceptable: 6", "the heavy compute passes with its score recorded")
    h.contains(printed, "Executing standard task", "a low-risk task runs unprompted")
    h.equal(printed.count("HUMAN INTERVENTION REQUIRED"), 1,
            "only the irreversible write asks for a human")

    h.write_json("result.json", {"agent": "AnalysisAgent", "gates": 1})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (risk-aware reporting)", FILES).crash())
