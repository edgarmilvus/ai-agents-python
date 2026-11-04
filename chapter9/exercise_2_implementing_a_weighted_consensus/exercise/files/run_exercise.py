"""Harness for exercise 2: weighted consensus."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

CHAPTER = ROOT / "chapter9"
SCAFFOLD = (CHAPTER / "unified_code_block_for_exercises_scaffold/example/files"
            / "01_exercise_scaffold.py")


def main():
    h = Harness("exercise 2 (weighted consensus)", FILES)
    solution = FILES / "01_weighted_consensus.py"
    source = SCAFFOLD.read_text() + "\n\n" + solution.read_text()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), {"__name__": "__main__"})
    printed = log.getvalue()

    h.contains(printed, "Consensus", "a consensus score is produced")
    h.contains(printed, "Refinement", "the advice is aggregated")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (weighted consensus)", FILES).crash())
