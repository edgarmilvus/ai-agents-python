"""Harness for exercise 5: the same question answered by CoT and by ReAct."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 5 (CoT vs ReAct)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_cot_vs_react.py", "cot_vs_react")
    printed = log.getvalue()

    h.check("Microsoft" in printed and "Apple" in printed,
            "the comparison names both candidates")
    h.check("3.15" in printed or "3,15" in printed, "the ReAct answer carries the current figure")
    h.contains(printed, "ReAct", "the analysis names the ReAct agent")
    h.check("Chain of Thought" in printed or "CoT" in printed,
            "the analysis names the CoT agent")
    h.check("Observation" in printed, "the analysis credits the observation step")
    h.check(len(printed) > 500, "the comparison is an analysis, not a one-line verdict")

    h.write_json("result.json", {
        "candidates": ["Apple", "Microsoft"],
        "react_answer": "Microsoft",
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (CoT vs ReAct)", FILES).crash())
