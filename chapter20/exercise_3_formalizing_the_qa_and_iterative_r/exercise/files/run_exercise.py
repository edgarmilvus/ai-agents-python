"""Harness for exercise 3: the QA refinement loop.

The section is one part of the chapter's capstone: it runs on the shared boilerplate,
plus the developer defined by exercise 2, and the harness loads those first, exactly as the book's Solutions section
reads them.
"""
import contextlib
import io
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
CHAPTER = FILES.parents[2]
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

BOILERPLATE = CHAPTER / "shared_boilerplate_models_and_base_agent/example/files/01_swarm_boilerplate.py"
ROLES = CHAPTER / "exercise_2_dynamic_role_assignment_middleware/exercise/files/01_role_router.py"

def load(path, base, extra=None):
    return dict(runpy.run_path(str(path), init_globals={**base, **(extra or {})}))


def main():
    h = Harness("exercise 3 (QA loop)", FILES)
    base = dict(runpy.run_path(str(BOILERPLATE)))
    roles = load(ROLES, base)
    globals_ = {**base, **roles}
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_qa_loop.py"), init_globals=globals_, run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "--- Refinement Cycle 1 ---", "the loop started")
    h.contains(printed, "Generating Bug Report", "the first artifact failed QA")
    h.contains(printed, "Routing Bug Report", "the bug report was routed back")
    h.contains(printed, "--- Refinement Cycle 2 ---", "the loop ran again")
    h.contains(printed, "Artifact passed QA", "the refined artifact passed")
    h.contains(printed, "[ORCHESTRATOR] SUCCESS", "the loop stopped on success")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (QA loop)", FILES).crash())
