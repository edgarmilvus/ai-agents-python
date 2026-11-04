"""Harness for the unified solution block: all five exercises in one run."""
import contextlib
import io
import os
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 3 (unified solution)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            runpy.run_path(str(FILES / "01_unified_solution.py"), run_name="__main__")
        printed = log.getvalue()

        h.contains(printed, "Routing Query", "queries were routed")
        h.contains(printed, "Code Store", "the code store was selected")
        h.contains(printed, "Docs Store", "the docs store was selected")
        h.check(printed.count("Routing Query") >= 2, "more than one query was routed")
        h.contains(printed, "Retrieval Result", "each route returned documents")

        h.write_json("result.json", {"queries": printed.count("Routing Query")})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (unified solution)", FILES).crash())
