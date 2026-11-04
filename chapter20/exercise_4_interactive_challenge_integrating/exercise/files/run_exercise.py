"""Harness for exercise 4: the security auditor in front of QA.

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
    h = Harness("exercise 4 (security auditor)", FILES)
    base = dict(runpy.run_path(str(BOILERPLATE)))
    roles = load(ROLES, base)
    qa = load(QA, base, roles)
    globals_ = {**base, **roles, **qa}
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_security_auditor.py"), init_globals=globals_, run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Auditing artifact:", "the auditor saw the artifact")
    h.contains(printed, "Security Audit", "the audit produced a verdict")
    h.contains(printed, "QA Bug Report received", "a QA failure was routed back")
    h.contains(printed, "SUCCESS: Artifact passed Security and QA", "the loop converged")
    h.contains(printed, "Final Artifact Delivered:", "the delivered artifact is printed")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (security auditor)", FILES).crash())
