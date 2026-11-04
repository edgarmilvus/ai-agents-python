"""Harness for exercise 1: research with a confidence loop."""
import contextlib
import io
import pathlib
import random
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

SEED = 1


def main():
    h = Harness("exercise 1 (research confidence)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_research_confidence.py", "ex841")
    printed = log.getvalue()

    h.contains(printed, "Final Confidence", "the run reports its final confidence")
    h.contains(printed, "Total Attempts", "the run reports how many attempts it took")
    h.check("Total Attempts: 2" in printed, "the loop stopped on the second attempt")
    h.contains(printed, "Total Documents: 5", "the research collected five documents")
    h.contains(printed, "Evaluation", "the confidence node ran")

    h.write_json("result.json", {"seed": SEED, "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (research confidence)", FILES).crash())
