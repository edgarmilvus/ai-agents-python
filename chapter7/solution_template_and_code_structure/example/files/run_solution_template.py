"""Harness for the solution template: all four exercises in one file."""
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
    h = Harness("example 4 (solution template)", FILES)
    install()
    module = load_listing(FILES / "01_solution_template.py", "solution_template")

    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        for number in range(1, 5):
            getattr(module, f"run_exercise_{number}")()
    printed = log.getvalue()

    for number in range(1, 5):
        h.contains(printed, f"[EXERCISE {number} RESULT]", f"exercise {number} produced a result")
    h.check(printed.count("SCRIPTED OUTPUT") >= 4, "each crew returned the model output")
    h.check(len(CALLS) >= 4, "all four crews consulted the model")
    h.equal(len({name for name in dir(module) if name.startswith("run_exercise_")}), 4,
            "the template defines exactly four entry points")

    h.write_json("result.json", {"exercises": 4, "calls": len(CALLS)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (solution template)", FILES).crash())
