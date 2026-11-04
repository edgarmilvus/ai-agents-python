"""Harness for exercise 5: a chatbot with tool retries."""
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
    h = Harness("exercise 5 (chatbot retries)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_chatbot_retries.py", "ex845")
    printed = log.getvalue()

    h.contains(printed, "Final Chat History", "the run prints the history")
    h.contains(printed, "Calculation successful", "the tool eventually answered")
    h.check("Result: 2" in printed or "Result: 1" in printed or "Result: 10" in printed,
            "the calculation returned a number")
    h.contains(printed, "User:", "the user turn is in the history")

    h.write_json("result.json", {"seed": SEED, "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (chatbot retries)", FILES).crash())
