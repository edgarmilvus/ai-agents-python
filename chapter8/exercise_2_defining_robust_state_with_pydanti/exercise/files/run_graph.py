"""Harness for exercise 2: a Pydantic state and its rejections."""
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
    h = Harness("exercise 2 (robust state)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_robust_state.py", "ex842")
    printed = log.getvalue()

    h.contains(printed, "Total items processed: 5", "all five items were processed")
    h.contains(printed, "Successful outputs: 4", "one item was rejected")
    h.contains(printed, "Errors logged", "the rejection is recorded")
    h.contains(printed, "Invalid format", "the error explains the rejection")

    h.write_json("result.json", {"seed": SEED, "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (robust state)", FILES).crash())
