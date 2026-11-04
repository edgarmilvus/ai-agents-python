"""Harness for the basic snapshot example: two runs, one growing history."""
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
    h = Harness("example 1 (state snapshot)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    state = output / "agent_state.pkl"
    if state.exists():
        state.unlink()
    previous = os.getcwd()
    os.chdir(output)
    try:
        first = io.StringIO()
        with contextlib.redirect_stdout(first):
            runpy.run_path(str(FILES / "01_state_snapshot.py"), run_name="__main__")
        second = io.StringIO()
        with contextlib.redirect_stdout(second):
            runpy.run_path(str(FILES / "01_state_snapshot.py"), run_name="__main__")

        h.contains(first.getvalue(), "Total Sessions Run: 0",
                   "the first run starts from an empty state")
        h.contains(second.getvalue(), "Total Sessions Run: 1",
                   "the second run sees the saved counter")
        h.contains(second.getvalue(), "History Log Length: 3",
                   "the saved history is reloaded")
        h.check(state.exists(), "the snapshot file is written")

        h.write_json("result.json", {"snapshot_bytes": state.stat().st_size})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (state snapshot)", FILES).crash())
