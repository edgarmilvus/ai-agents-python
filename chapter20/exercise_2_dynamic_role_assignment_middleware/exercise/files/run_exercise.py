"""Harness for exercise 2: the role-assignment middleware.

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
    h = Harness("exercise 2 (role router)", FILES)
    base = dict(runpy.run_path(str(BOILERPLATE)))
    globals_ = dict(base)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_role_router.py"), init_globals=globals_, run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Exercise 2 Demo", "the demo ran")
    h.contains(printed, "Load Balancing Results", "the results were reported")
    h.equal(printed.count("Completed task: Feature"), 9, "all nine tasks were routed")
    h.equal(printed.count("0 tasks remaining (should be 0)"), 3, "every developer drained its queue")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (role router)", FILES).crash())
