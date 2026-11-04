"""Harness for the shared boilerplate.

The models and the base agent are the vocabulary the five exercises share. The
harness checks the contracts the exercises rely on: the state defaults, the bug and
violation ids, and the two ways to submit work — the future, and the result.
"""
import asyncio
import importlib.util
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 4 (shared boilerplate)", FILES)
    spec = importlib.util.spec_from_file_location("swarm_boilerplate",
                                                  str(FILES / "01_swarm_boilerplate.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    state = module.ProjectState()
    h.equal(state.status, "REQUIREMENTS_GATHERING", "the default state is requirements")
    h.equal(state.bug_count, 0, "the bug count starts empty")

    bug = module.BugReport(severity="CRITICAL", description="crash",
                           steps_to_reproduce=["open", "click"],
                           suggested_fix_summary="guard the click")
    h.check(1000 <= bug.bug_id <= 9999, "a bug id lands in the expected range")
    violation = module.SecurityViolation(vulnerability_type="SQLi", risk_level="HIGH",
                                         vulnerable_code_snippet="SELECT *",
                                         remediation_instruction="use a parameterised query")
    h.check(500 <= violation.violation_id <= 999, "a violation id lands in the expected range")

    agent = module.BaseAgent("Dev_Test")

    async def scenario():
        worker = asyncio.create_task(agent.process_tasks())
        future = await agent.submit_task("Write the endpoint")
        by_future = await future
        by_result = await agent.run_task("Write it again")
        worker.cancel()
        return by_future, by_result

    by_future, by_result = asyncio.run(scenario())
    h.contains(by_future, "InitialCode", "awaiting the future returns the artifact")
    h.contains(by_result, "InitialCode", "run_task waits for the result, not the future")

    h.write_json("result.json", {"agent": agent.name})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (shared boilerplate)", FILES).crash())
