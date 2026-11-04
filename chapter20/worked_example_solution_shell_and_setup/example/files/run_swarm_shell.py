"""Harness for the solution shell.

The shell is a template: its driver is commented out and its monitoring loop never
ends, so the harness does not run `main()`. It imports the module and exercises the
pieces the exercises build on — the state hub, the roles, the supervisor.
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
    h = Harness("example 3 (solution shell)", FILES)
    spec = importlib.util.spec_from_file_location("swarm_shell", str(FILES / "01_swarm_shell.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    roles = ["SwarmStateHub", "DeveloperAgent", "QAAgent", "SecurityAuditorAgent",
             "SupervisorAgent", "TaskRouterMiddleware", "ProjectState", "BugReport"]
    missing = [name for name in roles if not hasattr(module, name)]
    h.equal(missing, [], "the shell defines every role the exercises extend")

    state = module.ProjectState()
    h.equal(state.status, "REQUIREMENTS_GATHERING", "the project starts in requirements")
    h.equal(state.version, 0, "the version starts at zero")

    async def scenario():
        hub = module.SwarmStateHub()
        waiter = asyncio.create_task(hub.wait_for_status("IN_DEVELOPMENT"))
        await asyncio.sleep(0.05)
        await hub.update_state({"status": "IN_DEVELOPMENT", "current_artifact": "Reqs_V1"})
        return await waiter

    handed = asyncio.run(scenario())
    h.equal(handed.status, "IN_DEVELOPMENT", "the waiter was woken by the transition")
    h.equal(handed.current_artifact, "Reqs_V1", "the artifact travelled with the state")
    h.equal(handed.version, 1, "each update bumps the version")

    report = module.BugReport(severity="MAJOR", description="x", steps_to_reproduce=["1"],
                              suggested_fix_summary="fix")
    h.check(1000 <= report.bug_id <= 9999, "a bug report gets an id")

    h.write_json("result.json", {"roles": roles})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (solution shell)", FILES).crash())
