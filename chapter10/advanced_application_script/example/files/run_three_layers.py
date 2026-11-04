"""Harness for the three-layer persistence agent: JSON, SQLite and Chroma."""
import contextlib
import io
import os
import pathlib
import runpy
import sys
import warnings

# Silence warnings before importing: they carry absolute paths, and the log must
# not. The second call is needed because langchain installs its own filters when
# it imports.
warnings.simplefilter("ignore")
import langchain_classic.memory  # noqa: E402,F401
import langchain_community.vectorstores  # noqa: E402,F401

warnings.simplefilter("ignore")

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 2 (three layers)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        # Warnings from the langchain imports carry absolute paths; they are not
        # part of the verdict, so stderr is dropped for the run.
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(io.StringIO()):
            runpy.run_path(str(FILES / "01_three_layer_persistence.py"), run_name="__main__")
        printed = log.getvalue()

        h.contains(printed, "SESSION 1", "the first session ran")
        h.contains(printed, "SESSION 2 (New Process)", "the second session is a new process")
        h.contains(printed, "History Loaded: 2 previous turns", "SQLite history was reloaded")
        h.contains(printed, "Semantic Store Initialized/Loaded", "the vector store was opened")
        h.contains(printed, "Semantic Retrieval Test", "semantic retrieval ran")
        h.contains(printed, "All persistence layers committed", "the state was saved")
        h.contains(printed, "Persistence Files Cleaned Up",
                   "the demo removes its files after the second session")
        h.check(not pathlib.Path("agent_config.json").exists(),
                "no JSON layer is left behind")

        h.write_json("result.json", {"layers": ["json", "sqlite", "chroma"]})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (three layers)", FILES).crash())
