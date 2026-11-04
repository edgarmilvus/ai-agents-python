"""Harness for exercise 1: the resource collector's OODA loop.

The environment is random, so the harness seeds it: the same seed must produce
the same run, which is what makes the statements about the loop checkable.
"""
import contextlib
import io
import pathlib
import random
import re
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

SEED = 7
OBSERVE_RE = re.compile(r"\[Observe\] Available resources detected: (\d+)")


def run_with_capture(listing, seed):
    random.seed(seed)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        listing.run_resource_agent()
    return buffer.getvalue()


def main():
    h = Harness("exercise 1 (OODA loop)", FILES)
    listing = load_listing(FILES / "01_ooda_resource_collector.py", "ooda_collector")

    log = run_with_capture(listing, SEED)
    observations = [int(match) for match in OBSERVE_RE.findall(log)]

    h.check(len(observations) >= 3, "the loop observes at least three times")
    h.check(all(1 <= value <= 5 for value in observations),
            "every observation is inside the environment's 1-5 range")
    h.contains(log, "Termination signal received",
               "the loop ends because the agent decides to terminate")

    # OODA is an order, not a set: within one iteration each phase precedes the
    # next, and Act returns control to Observe.
    first = log.split("--- Iteration 2 ---")[0]
    phases = ["[Observe]", "[Orient]", "[Decide]", "[Act]"]
    positions = [first.find(phase) for phase in phases]
    h.check(all(position >= 0 for position in positions),
            "the first iteration runs all four phases")
    h.equal(positions, sorted(positions), "the first iteration runs them in OODA order")

    # The result of Act is the input of the next Observe: the running total is
    # the sum of the collections, and the observation drawn by the terminating
    # pass is seen but never collected.
    totals = [int(value) for value in re.findall(r"New total: (\d+)", log)]
    h.equal(totals[-1], sum(observations[:-1]),
            "the final total is the sum of the observations acted on")
    h.check(totals[-1] >= 10, "the loop stops only once the goal is met")
    h.equal(totals, sorted(totals), "the resource count never decreases")

    # Same seed, same run: the loop's decisions are a function of its inputs.
    log_again = run_with_capture(listing, SEED)
    h.equal(OBSERVE_RE.findall(log_again), OBSERVE_RE.findall(log),
            "the same seed reproduces the same episode")

    h.write_json("result.json", {
        "seed": SEED,
        "goal": 10,
        "observations": observations,
        "collected": sum(observations),
        "iterations": len(observations),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (OODA loop)", FILES).crash())
