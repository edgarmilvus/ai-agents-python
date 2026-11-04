"""Harness for exercise 1: structured CoT with an explicit audit trail."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 1 (structured CoT)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_structured_cot.py", "structured_cot")
    printed = log.getvalue()

    prompt = module.create_structured_cot_prompt("A: test scenario")
    h.contains(prompt, "A: test scenario", "the prompt receives the scenario it is given")
    for header in ["---STEP 1: Material Analysis---", "---STEP 2: Logistics Analysis---",
                   "---STEP 3: Financial Analysis---", "---SYNTHESIS & CONCLUSION---"]:
        h.contains(prompt, header, f"the prompt fixes the header {header}")

    h.contains(printed, "---ASSUMPTIONS---", "the answer keeps the required sections")
    h.contains(printed, "Location B", "the recommendation is the highest weighted score")
    h.contains(printed, "Justification Score: 60/100", "the score is expressed out of 100")
    h.contains(printed, "Transport", "the reasoning names the criterion that decided it")

    h.write_json("result.json", {
        "headers": ["ASSUMPTIONS", "STEP 1", "STEP 2", "STEP 3", "SYNTHESIS"],
        "recommendation": "Location B",
        "score": "60/100",
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (structured CoT)", FILES).crash())
