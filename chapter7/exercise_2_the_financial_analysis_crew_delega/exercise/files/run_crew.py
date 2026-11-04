"""Harness for exercise 2: delegation with structured output."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402
from scripted_crew import CALLS, install  # noqa: E402


def main():
    h = Harness("exercise 2 (financial crew)", FILES)
    install()
    module = load_listing(FILES / "01_financial_crew.py", "ex2_crew")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module.run_exercise_2()
    printed = log.getvalue()

    h.contains(printed, "[EXERCISE 2 RESULT]", "the crew printed its result")
    h.contains(printed, "SCRIPTED OUTPUT", "the result is the model output")
    h.check(len(CALLS) >= 1, "the crew consulted the model")
    h.contains(printed, "Risk Report", "the output is labelled as the risk report")

    h.write_json("result.json", {"calls": len(CALLS), "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (financial crew)", FILES).crash())
