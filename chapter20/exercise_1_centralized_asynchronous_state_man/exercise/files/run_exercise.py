"""Harness for exercise 1: the centralised state hub.

The section is one part of the chapter's capstone: it runs on the shared boilerplate,
and nothing else, and the harness loads those first, exactly as the book's Solutions section
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


def load(path, base, extra=None):
    return dict(runpy.run_path(str(path), init_globals={**base, **(extra or {})}))


def main():
    h = Harness("exercise 1 (state hub)", FILES)
    base = dict(runpy.run_path(str(BOILERPLATE)))
    globals_ = dict(base)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_state_hub.py"), init_globals=globals_, run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Starting Exercise 1 Demo: Future-Based State Handoff",
               "the demo ran")
    h.contains(printed, "[HUB] State updated to: IN_DEVELOPMENT (V1)",
               "the product owner moved the state")
    h.contains(printed, "[DEV Agent] Signal received. Starting work on artifact: Reqs_Final_V1",
               "the developer was woken with the artifact")
    h.contains(printed, "Starting fix cycle. Current Bug Count: 5",
               "the QA failure woke the developer again")
    h.contains(printed, "Exercise 1 Demo Complete", "the handoff closed cleanly")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (state hub)", FILES).crash())
