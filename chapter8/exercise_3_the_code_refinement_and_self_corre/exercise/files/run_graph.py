"""Harness for exercise 3: a self-correcting code loop."""
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
    h = Harness("exercise 3 (code refinement)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_code_refinement.py", "ex843")
    printed = log.getvalue()

    h.contains(printed, "Attempt 3. Result: PASS", "the third attempt passes")
    h.contains(printed, "Attempt 2. Result: FAIL", "the second attempt still fails")
    h.contains(printed, "Debugger", "the debugger node ran")
    h.contains(printed, "Generator", "the generator node ran")

    h.write_json("result.json", {"seed": SEED, "printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (code refinement)", FILES).crash())
