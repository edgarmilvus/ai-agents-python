"""Harness for exercise 4: the financial analyst graph."""
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
    h = Harness("exercise 4 (financial analyst)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_financial_analyst.py", "ex844")
    printed = log.getvalue()

    h.contains(printed, "Research", "the research node ran")
    h.contains(printed, "Risk Drafter", "the risk section was added")
    h.contains(printed, "Finalize", "the graph finalised the report")
    h.contains(printed, "complete", "the final state says the report is complete")

    h.write_json("result.json", {"seed": SEED, "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (financial analyst)", FILES).crash())
