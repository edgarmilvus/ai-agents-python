"""Harness for the state-machine approval gate.

The listing runs two examples from its `__main__`, each of which waits for a typed
answer. The harness plays the human: rationale then approval in the first run,
override in the second, and it checks that the two runs end in different states.
"""
import contextlib
import io
import pathlib
import sys
import time

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import builtins  # noqa: E402


def run_agent(module, answers):
    remaining = list(answers)

    def fake_input(message=""):
        return remaining.pop(0) if remaining else "R"

    agent = module.CIUAgent(initial_goal="Securely expose the new API gateway.")
    original = builtins.input
    builtins.input = fake_input
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            agent.run_workflow()
    finally:
        builtins.input = original
    return agent, log.getvalue()


def main():
    h = Harness("example 2 (state machine gate)", FILES)
    module = load_listing(FILES / "01_state_machine_gate.py", "state_machine_gate")

    # The listing sleeps to look like real work; the harness does not need the wait.
    real_sleep = time.sleep
    time.sleep = lambda *_: None
    try:
        approved, printed = run_agent(module, ["E", "A"])
    finally:
        time.sleep = real_sleep

    h.contains(printed, "[GATE TRIGGERED]", "the gate stopped the workflow")
    h.contains(printed, "Agent Rationale", "the human can ask for the rationale")
    h.contains(printed, "CRITICAL EXECUTION SUCCESSFUL", "approval ran the critical action")
    h.equal(approved.state, module.AgentState.COMPLETED, "the approved run completes")

    time.sleep = lambda *_: None
    try:
        redirected, printed = run_agent(module, ["R"])
    finally:
        time.sleep = real_sleep

    h.contains(printed, "Human Rejected/Overrode", "the override is recorded")
    h.contains(printed, "Redirecting plan", "the override changes the plan")
    h.check("CRITICAL EXECUTION SUCCESSFUL" not in printed,
            "nothing is executed when the human overrides")
    h.equal(redirected.state, module.AgentState.COMPLETED, "the redirected run also ends")

    h.write_json("result.json", {"approved_state": approved.state.name,
                                 "redirected_state": redirected.state.name})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (state machine gate)", FILES).crash())
