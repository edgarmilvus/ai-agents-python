"""Harness for exercise 4: semantic scoring."""
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
    h = Harness("exercise 4 (semantic review)", FILES)
    solution = FILES / "01_semantic_review.py"
    source = SCAFFOLD.read_text() + "\n\n" + solution.read_text()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), {"__name__": "__main__"})
    printed = log.getvalue()

    h.contains(printed, "Semantic", "the semantic adjustment runs")
    h.contains(printed, "Adjusted Consensus Score", "the adjusted score is reported")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (semantic review)", FILES).crash())
