"""Harness for the self-correcting validation agent.

The agent is deterministic (the "LLM" is a state machine), so the harness can
assert the whole path: a validation that fails on two rules, a correction that
acts on the error report, and a second validation that passes.
"""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

BAD_PROPOSAL = {
    "title": (
        "A Very Long Project Title That Exceeds The Maximum Character Count "
        "Allowed By The Strict Formatting Rules For The Proposal Submission System"
    ),
    "description": "Short description.",
}


def main():
    h = Harness("example 2 (validation agent)", FILES)
    listing = load_listing(
        FILES / "01_self_correcting_validation_agent.py", "validation_agent"
    )

    state = listing.run_validation_agent(dict(BAD_PROPOSAL))

    h.equal(state["status"], "GOAL_MET", "the agent ends with the goal met")
    h.equal(state["iteration"], 3, "the path is validate, correct, validate")
    h.equal([step["action"] for step in state["history"]],
            ["validate", "correct", "validate"],
            "every iteration recorded the tool it chose")
    h.equal(state["history"][0]["status_after"], "FAILED_VALIDATION",
            "the first validation fails")
    h.equal(len(state["last_errors"]), 2, "both broken rules are reported")
    h.check(any("Title length" in error for error in state["last_errors"]),
            "the report names the title rule")
    h.check(any("Description length" in error for error in state["last_errors"]),
            "the report names the description rule")

    # Re-check the rules independently of the agent's own validator.
    final = listing.ProjectProposal(**state["current_proposal"])
    h.check(10 <= len(final.title) <= 50, "the final title is inside 10-50 characters")
    h.check(len(final.description) >= 100,
            "the final description reaches the 100-character minimum")
    h.equal(final.title, BAD_PROPOSAL["title"][:50], "the title was truncated, not rewritten")

    again = listing.run_validation_agent(dict(BAD_PROPOSAL))
    h.equal(again["current_proposal"], state["current_proposal"],
            "the run is reproducible")

    h.write_json("final_state.json", {
        "status": state["status"],
        "iterations": state["iteration"],
        "actions": [step["action"] for step in state["history"]],
        "errors_after_first_validation": state["last_errors"],
        "final_proposal": state["current_proposal"],
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (validation agent)", FILES).crash())
