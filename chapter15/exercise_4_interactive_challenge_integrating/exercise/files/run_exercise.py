"""Harness for exercise 4: static analysis before execution.

The style check is the part worth testing directly, so the harness runs it on
three snippets and then drives the extended loop through its three attempts:
style failure, execution failure, success.
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
    h = Harness("exercise 4 (static analysis)", FILES)
    module = load_listing(FILES / "01_static_analysis.py", "static_analysis")
    check = module.check_style_compliance

    compliant, errors = check("def calculate_sum(a, b):\n    total_value = a + b\n    return total_value")
    h.equal(compliant, True, "snake_case passes")
    h.equal(errors, [], "a compliant snippet has no findings")

    compliant, errors = check("def CalculateSum(a, b):\n    return a + b")
    h.equal(compliant, False, "a CamelCase function fails")
    h.contains(errors[0], "CalculateSum", "the offender is named")

    compliant, errors = check("def f():\n    myValue = 1\n    return myValue")
    h.equal(compliant, False, "a mixed-case variable fails")

    orchestrator = module.ExtendedOrchestrator(
        initial_prompt="Write a function for summation, ensuring PEP 8 compliance.",
        max_attempts=5)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        final = orchestrator.run_loop()
    printed = log.getvalue()

    h.contains(printed, "[STYLE FAILURE]", "the first attempt was stopped by the linter")
    h.contains(printed, "Skipping execution", "the sandbox was skipped for a style error")
    h.contains(printed, "[STYLE SUCCESS]", "the corrected code passed the linter")
    h.contains(printed, "[EXECUTION FAILURE]", "the second attempt failed in the sandbox")
    h.contains(printed, "[SUCCESS] Code passed all tests", "the third attempt passed")
    h.equal(orchestrator.current_attempt, 3, "it took three attempts")
    h.check(final is not None, "the loop returned the passing package")

    h.write_json("result.json", {"attempts": orchestrator.current_attempt})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (static analysis)", FILES).crash())
