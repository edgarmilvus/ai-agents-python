"""Harness for exercise 2: dynamic interruption and redirection.

The operator pauses the flagged task; the harness asserts the queue resumes
where it stopped and then drains."""
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
SOLUTION = FILES / "01_interruption_agent.py"


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
    h = Harness("exercise 2 (interruption and redirection)", FILES)
    ns, printed = compose()
    h.contains(printed, "INTERRUPTION", "the flagged task stops the queue")
    h.contains(printed, "Resuming task", "the pause resumes the same task")
    h.contains(printed, "finished execution", "the queue drains afterwards")

    h.write_json("result.json", {"agent": "DataMigrationAgent", "interrupt": "resume"})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (interruption and redirection)", FILES).crash())
