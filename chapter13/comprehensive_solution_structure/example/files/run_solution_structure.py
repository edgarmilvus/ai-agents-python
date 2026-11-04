"""Harness for the comprehensive solution structure: the shape of the four agents."""
import contextlib
import io
import pathlib
import sys
import time

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

import builtins  # noqa: E402


def answer(message: str) -> str:
    text = str(message)
    if "Authorization Code" in text:
        return "PROD_OVERSEER_2024"
    if "(P/S/R)" in text:
        return "P"
    if "new comma-separated" in text:
        return "fileA,fileB"
    if "Y/N" in text:
        return "Y"
    return ""


def drive(agent):
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        agent.run()
    return log.getvalue()


def main():
    h = Harness("example 3 (solution structure)", FILES)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hitl_structure", str(FILES / "01_solution_structure.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    agents = sorted(name for name in dir(module)
                    if name.endswith("Agent") and name[0].isupper() and name != "AgentState")
    h.equal(agents, ["AnalysisAgent", "ConfigAgent", "DataMigrationAgent", "DeploymentAgent"],
            "the structure defines the four agents")

    original_input = builtins.input
    real_sleep = time.sleep
    builtins.input = lambda message="": answer(message)
    time.sleep = lambda *_: None
    try:
        printed = drive(module.ConfigAgent())
        h.contains(printed, "Stage 1", "the first agent reaches its planning stage")
        h.contains(printed, "Human Approved", "the gate accepted the human approval")

        printed = drive(module.AnalysisAgent())
        h.contains(printed, "Current State: AWAITING_APPROVAL",
                   "the risk gate shows the agent's state")
        h.contains(printed, "Recent Agent History", "the gate shows the context buffer")
    finally:
        builtins.input = original_input
        time.sleep = real_sleep

    h.write_json("result.json", {"agents": agents})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (solution structure)", FILES).crash())
