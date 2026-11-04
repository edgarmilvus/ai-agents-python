"""Harness for exercise 5: the self-healing supervisor.

The section is one part of the chapter's capstone: it runs on the shared boilerplate,
plus the developer and the QA agent from exercises 2 and 3, and the harness loads those first, exactly as the book's Solutions section
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
QA = CHAPTER / "exercise_3_formalizing_the_qa_and_iterative_r/exercise/files/01_qa_loop.py"

def load(path, base, extra=None):
    return dict(runpy.run_path(str(path), init_globals={**base, **(extra or {})}))


def main():
    h = Harness("exercise 5 (self-healing swarm)", FILES)
    base = dict(runpy.run_path(str(BOILERPLATE)))
    roles = load(ROLES, base)
    qa = load(QA, base, roles)
    globals_ = {**base, **roles, **qa}
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_self_healing.py"), init_globals=globals_, run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Starting health monitoring", "the supervisor started")
    h.contains(printed, "CRITICAL: Dev_Alpha timed out", "the failure was detected")
    h.contains(printed, "Provisioning new instance", "a replacement was created")
    h.contains(printed, "Task result: Completed task", "the replacement does real work")
    h.contains(printed, "Exercise 5 Demo Complete", "the demo closed cleanly")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (self-healing swarm)", FILES).crash())
