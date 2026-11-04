"""Harness for exercise 5's hint block: the mocked RAG infrastructure."""
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
    h = Harness("exercise 5 (multi-vector hint)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            runpy.run_path(str(FILES / "01_multi_vector_hint.py"), run_name="__main__")
        printed = log.getvalue()

        h.contains(printed, "Exercise 1", "the chunking exercise ran")
        h.contains(printed, "Exercise 2", "the filtering exercise ran")
        h.contains(printed, "Router selected", "the router chose a store")
        h.check(printed.count("Chunk") >= 2, "the document was split into chunks")

        h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 5 (multi-vector hint)", FILES).crash())
