"""Harness for the cost tracker.

The listing simulates three agent calls and prints what each one cost. The harness
checks the arithmetic directly — the rates are per million tokens, the estimate is
one token per four characters — and then checks that the printed transactions add up
to the printed total.
"""
import contextlib
import io
import pathlib
import re
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("example 1 (cost tracker)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        ns = runpy.run_path(str(FILES / "01_cost_tracker.py"), run_name="__main__")
        tracker = ns["AsyncLLMCostTracker"]("test_model")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Cost Tracker initialized using rates: Input=$5.0/M, Output=$15.0/M",
               "the tracker reports the rates it will use")
    h.equal(printed.count("-> S"), 5, "three calls printed their usage and cost")
    h.contains(printed, "TOTAL ESTIMATED COST:", "the report totals the cost")

    h.equal(tracker._estimate_tokens(""), 1, "an empty prompt still costs one token")
    h.equal(tracker._estimate_tokens("a" * 40), 10, "the estimate is one token per four characters")
    h.equal(tracker._calculate_cost(1_000_000, 0), 5.0, "a million input tokens cost the input rate")
    h.equal(tracker._calculate_cost(0, 1_000_000), 15.0, "a million output tokens cost the output rate")

    transactions = [float(value) for value in re.findall(r"-> S\d Cost: \$([0-9.]+)", printed)]
    total = float(re.search(r"TOTAL ESTIMATED COST: \$([0-9.]+)", printed).group(1))
    h.equal(len(transactions), 3, "each call printed its cost")
    h.equal(round(sum(transactions), 8), round(total, 8), "the transactions add up to the total")

    tokens = [int(value) for value in re.findall(r"-> S\d Usage: Input=(\d+) \| Output=(\d+)", printed) for value in value]
    h.check(all(token > 0 for token in tokens), "every call consumed tokens")

    h.write_json("result.json", {"total_cost": total, "transactions": transactions})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (cost tracker)", FILES).crash())
