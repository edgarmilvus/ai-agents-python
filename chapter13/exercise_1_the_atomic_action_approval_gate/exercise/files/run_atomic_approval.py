"""Harness for exercise 1: the atomic action approval gate.

The book publishes the agent against the shared block, so the harness prepends it
and answers the gate as a scripted operator would."""
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
SOLUTION = FILES / "01_atomic_approval_agent.py"


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
    h = Harness("exercise 1 (atomic approval gate)", FILES)
    ns, printed = compose()
    h.contains(printed, "CRITICAL ACTION APPROVAL REQUIRED", "the change asks before it is applied")
    h.contains(printed, "Human Approved", "the approval is recorded before execution")
    h.contains(printed, "applied successfully", "the change reaches its terminal state")
    h.contains(printed, "EXECUTION IN PROGRESS", "the approved change reaches execution")

    h.write_json("result.json", {"agent": "ConfigAgent", "gate": "approved"})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (atomic approval gate)", FILES).crash())
