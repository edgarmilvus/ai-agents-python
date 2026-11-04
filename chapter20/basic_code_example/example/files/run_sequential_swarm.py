"""Harness for the sequential swarm.

The listing runs two demonstrations at import: one that delivers and one where the
QA gate rejects the artifact and the orchestrator halts. The harness checks both,
because the halt is the lesson.
"""
import contextlib
import io
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 1 (sequential swarm)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_sequential_swarm.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Starting Swarm Execution", "the orchestrator started")
    h.contains(printed, "[Agent_P1]: Initialized as Idea Generator", "the first role was instantiated")
    h.contains(printed, "[Agent_F1]: Initialized as Formatter", "the second role was instantiated")
    h.contains(printed, "Swarm execution successful. Final Deliverable:", "the handoff delivered")
    h.contains(printed, "Code the Future, Learn the Machine.", "the formatted artifact is the answer")
    h.contains(printed, "Execution halted due to agent feedback", "the second run was stopped")
    h.contains(printed, "Generation quality too low", "the halt names the reason")
    h.contains(printed, "Aborting delivery.", "nothing was delivered after the halt")

    h.write_json("result.json", {"delivered": True, "halted": True})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (sequential swarm)", FILES).crash())
