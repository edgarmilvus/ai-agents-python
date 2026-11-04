"""Harness for exercise 1: a sequential content crew."""
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
    h = Harness("exercise 1 (content crew)", FILES)
    install()
    module = load_listing(FILES / "01_content_crew.py", "ex1_crew")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module.run_exercise_1()
    printed = log.getvalue()

    h.contains(printed, "[EXERCISE 1 RESULT]", "the crew printed its result")
    h.contains(printed, "SCRIPTED OUTPUT", "the result is the model output")
    h.check(len(CALLS) >= 1, "the crew consulted the model")
    h.contains(printed, "Article Introduction", "the output is labelled as the article")

    h.write_json("result.json", {"calls": len(CALLS), "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (content crew)", FILES).crash())
