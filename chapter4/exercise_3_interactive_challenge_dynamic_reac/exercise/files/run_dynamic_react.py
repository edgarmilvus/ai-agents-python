"""Harness for exercise 3: self-correction driven by the quality of an observation."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 3 (dynamic ReAct)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_dynamic_react.py", "dynamic_react")
    printed = log.getvalue()

    h.contains(printed, "STEP 1", "the trace starts with a plan")
    h.contains(printed, "STEP 2", "the trace refines the query")
    h.contains(printed, "STEP 3", "the trace synthesises after the second observation")
    h.contains(printed, "SME", "the final answer is about the query's subject")
    h.check(printed.lower().count("observation") >= 2,
            "two observations are fed back into the loop")
    h.check("refine" in printed.lower() or "narrow" in printed.lower(),
            "the low-quality observation triggers a refinement")

    h.write_json("result.json", {
        "steps": 3,
        "observations": printed.lower().count("observation"),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (dynamic ReAct)", FILES).crash())
