"""Harness for the basic approval gate.

The listing blocks on `input()` in a worker thread, so the harness plays the human:
once asking for a status report, then approving. A second run aborts.
"""
import asyncio
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import builtins  # noqa: E402


def run_with_answers(module, answers):
    remaining = list(answers)

    def fake_input(message=""):
        return remaining.pop(0) if remaining else "ABORT"

    original = builtins.input
    builtins.input = fake_input
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            asyncio.run(module.agent_workflow())
    finally:
        builtins.input = original
    return log.getvalue()


def main():
    h = Harness("example 1 (approval gate)", FILES)
    module = load_listing(FILES / "01_approval_gate.py", "approval_gate")

    approved = run_with_answers(module, ["STATUS", "APPROVE"])
    h.contains(approved, "[CRITICAL APPROVAL REQUIRED]", "the gate stopped the workflow")
    h.contains(approved, "[AGENT STATUS REPORT]", "the status interruption was answered")
    h.contains(approved, "[HUMAN APPROVED]", "approval resumed the workflow")
    h.contains(approved, "Deployment Successful", "the critical action ran")

    aborted = run_with_answers(module, ["ABORT"])
    h.contains(aborted, "[HUMAN ABORTED]", "an abort stops the workflow")
    h.contains(aborted, "Rollback", "the abort path cleans up")
    h.check("Deployment Successful" not in aborted,
            "nothing is deployed when the human aborts")

    h.write_json("result.json", {"approved": True, "aborted": True})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (approval gate)", FILES).crash())
