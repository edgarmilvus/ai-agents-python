"""Harness for the exercise pipeline: config, state and history in one run."""
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
    h = Harness("example 3 (persistence pipeline)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    # Start from a clean slate: the listing persists a pickle and a SQLite file
    # here, and a leftover pair changes what the demonstration prints.
    for leftover in ("agent_config.pkl", "agent_history.db"):
        try:
            (output / leftover).unlink()
        except OSError:
            pass
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            runpy.run_path(str(FILES / "01_persistence_pipeline.py"), run_name="__main__")
        printed = log.getvalue()

        h.contains(printed, "Configuration loaded", "the JSON layer was read")
        h.contains(printed, "Agent State Loaded", "the pickled state was restored")
        h.contains(printed, "Success Rate", "the agent reports its counters")
        h.contains(printed, "Interaction 1 Complete", "the first interaction finished")
        h.check(pathlib.Path("agent_config.pkl").exists(), "the pickled config is on disk")
        h.check(pathlib.Path("agent_history.db").exists(), "the SQLite history is on disk")

        h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (persistence pipeline)", FILES).crash())
