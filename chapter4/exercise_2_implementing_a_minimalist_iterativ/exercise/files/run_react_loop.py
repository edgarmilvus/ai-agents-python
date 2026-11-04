"""Harness for exercise 2: a ReAct loop that must keep observing until a target state.

The tool is random by design, so the harness seeds it and requires the loop to
reach the target — status Operational and load under 50% — rather than stopping at
the first answer.
"""
import contextlib
import io
import pathlib
import random
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

SEED = 3


def main():
    h = Harness("exercise 2 (minimal ReAct loop)", FILES)
    random.seed(SEED)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "02_react_agent.py", "react_loop")
    printed = log.getvalue()

    h.contains(printed, "STEP 1", "the loop prints its first reasoning step")
    h.contains(printed, "Observation:", "the loop feeds observations back in")
    h.contains(printed, "Operational", "the run reaches an operational state")
    h.contains(printed, "Monitoring complete", "the loop terminates with a final answer")
    h.check("Load: 15%" in printed or "Load: 1" in printed or "Load: 2" in printed
            or "Load: 3" in printed or "Load: 4" in printed,
            "the final observation is under the 50% threshold")
    h.check(printed.count("Observation:") >= 2,
            "the agent observed more than once before answering")

    status = module.check_server_status("SRV-001")
    h.contains(status, "SRV-001", "the tool reports on the server it was asked about")

    h.write_json("result.json", {
        "seed": SEED,
        "observations": printed.count("Observation:"),
        "reached_target": "Operational" in printed and "Monitoring complete" in printed,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (minimal ReAct loop)", FILES).crash())
