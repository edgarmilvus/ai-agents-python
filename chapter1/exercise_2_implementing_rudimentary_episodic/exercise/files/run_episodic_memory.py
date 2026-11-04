"""Harness for exercise 2: episodic memory driving the next decision.

The 30% failure rate is seeded so the branch that matters is guaranteed to run:
a failed task must be followed by a review, and only then by a retry.
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

SEED = 1  # produces two failures, so both the review and the retry are exercised
TASKS = ["Task A: Data Ingestion", "Task B: Model Training", "Task C: Deployment"]


def run_with_capture(listing, seed):
    random.seed(seed)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        listing.run_task_agent()
    return buffer.getvalue()


def main():
    h = Harness("exercise 2 (episodic memory)", FILES)
    listing = load_listing(FILES / "01_episodic_memory_task_agent.py", "episodic_memory")

    h.check(hasattr(listing, "random"),
            "the listing imports random itself instead of borrowing it")

    log = run_with_capture(listing, SEED)

    h.contains(log, "All Tasks Completed Successfully", "the agent finishes the sequence")
    h.check(log.count("Performing mandatory review") >= 1,
            "a failed task triggers the review action")
    h.check(log.count("Performing mandatory review") == log.count("FAILED"),
            "every failure is reviewed once")

    # The shape of the branch: a failure, then a review, then a retry. The review
    # is announced by the Orient phase reading the failure out of memory, and
    # the retry arrives once the review has recorded a success.
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    reviewed = 0
    for index, line in enumerate(lines):
        if "Performing mandatory review" in line:
            reviewed += 1
            h.check(index > 0 and lines[index - 1] == "[Orient] Previous task failed. Prioritizing self-correction.",
                    "the review follows an Orient that read the failure from memory")
            h.check(any("Attempting:" in candidate for candidate in lines[index:index + 4]),
                    "the retry follows the review")
    h.check(reviewed >= 1, "at least one review was checked")

    # Reviews never advance the sequence, so the last task is still the last one.
    h.contains(log, "[Memory] Recorded: Task C: Deployment -> Success",
               "the sequence ends by recording the third task as a success")

    log_again = run_with_capture(listing, SEED)
    h.equal(log_again, log, "the same seed reproduces the same episode")

    h.write_json("result.json", {
        "seed": SEED,
        "tasks": TASKS,
        "failures": log.count("FAILED"),
        "reviews": reviewed,
        "log": log.splitlines(),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (episodic memory)", FILES).crash())
