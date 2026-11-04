"""Harness for exercise 3: the refinement loop.

The scripted model fails once and fixes the code from the feedback; the executor
fails on odd attempts. The harness checks that the loop reports the first failure,
feeds it back, and stops on the second attempt.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 3 (orchestrator)", FILES)
    module = load_listing(FILES / "01_orchestrator.py", "orchestrator")

    orchestrator = module.RefinementOrchestrator(
        initial_prompt="Write a function `calculate_sum(a, b)`.", max_attempts=4)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        final = orchestrator.run_loop()
    printed = log.getvalue()

    h.contains(printed, "--- Attempt 1 ---", "the first attempt ran")
    h.contains(printed, "Initial implementation", "the generator started from scratch")
    h.contains(printed, "[FAILURE] Reason: Test Failure", "the executor reported the failure")
    h.contains(printed, "--- Attempt 2 ---", "the loop tried again")
    h.contains(printed, "Correcting previous execution error", "the feedback reached the generator")
    h.contains(printed, "[SUCCESS] Code passed all tests", "the second attempt passed")
    h.equal(orchestrator.current_attempt, 2, "the loop stopped as soon as it passed")
    h.check(final is not None, "the loop returned the passing package")
    h.contains(final.function_code.code_string, "def calculate_sum", "the package carries the code")

    h.write_json("result.json", {"attempts": orchestrator.current_attempt})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (orchestrator)", FILES).crash())
