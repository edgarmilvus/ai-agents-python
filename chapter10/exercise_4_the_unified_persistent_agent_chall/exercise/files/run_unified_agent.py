"""Harness for the unified persistent agent: history, state and semantic recall."""
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
    h = Harness("exercise 4 (unified agent)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    # The listing persists its state here, so a previous run would be resumed
    # instead of demonstrated. Remove only the artefacts it owns: the folder also
    # holds `harness.log`, which the shell runner writes and then greps.
    for leftover in ("agent_config.pkl", "agent_history.db", "harness.log.bak"):
        try:
            (output / leftover).unlink()
        except OSError:
            pass
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            runpy.run_path(str(FILES / "01_unified_persistent_agent.py"), run_name="__main__")
        printed = log.getvalue()

        h.contains(printed, "Interaction 1", "the first interaction ran")
        h.contains(printed, "[USER]:", "the user turn is printed")
        h.contains(printed, "[AGENT]:", "the agent answered")
        h.contains(printed, "[SEMANTIC]", "semantic retrieval is exercised")
        h.contains(printed, "Tasks Completed", "the persisted counters are reported")
        h.check(printed.count("--- Interaction") >= 2, "more than one interaction ran")

        h.write_json("result.json", {"interactions": printed.count("--- Interaction")})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (unified agent)", FILES).crash())
