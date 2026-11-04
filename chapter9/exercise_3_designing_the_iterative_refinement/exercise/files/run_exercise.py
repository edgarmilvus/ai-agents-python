"""Harness for exercise 3: the refinement loop."""
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
    h = Harness("exercise 3 (refinement loop)", FILES)
    solution = FILES / "01_refinement_loop.py"
    source = SCAFFOLD.read_text() + "\n\n" + solution.read_text()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), {"__name__": "__main__"})
    printed = log.getvalue()

    h.contains(printed, "Loop Finished", "the loop terminates")
    h.contains(printed, "Final Score", "the final score is reported")
    h.contains(printed, "Iterations", "the iteration count is reported")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (refinement loop)", FILES).crash())
