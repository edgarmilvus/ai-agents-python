"""Harness for the reference shells: all four exercises in one script."""
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
    h = Harness("example 3 (solution shells)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_solution_shells.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    # exercise 1: budget success and budget breach
    h.contains(printed, "Running Exercise 1: Token Budget Manager (Success Case)",
               "the success case ran")
    h.contains(printed, "[SUCCESS] Context finished. Final token usage: 75",
               "the short run stayed inside its budget")
    h.contains(printed, "Budget breach detected", "the long run was stopped")
    h.contains(printed, "Caught expected error:", "the breach was caught")

    # exercise 2: the trimming goal
    saving = float(re.search(r"Percentage Cost Saving for LLM Input: ([0-9.]+)%", printed).group(1))
    h.check(saving >= 60, f"trimming reached {saving:.2f}% (needs 60%)")

    # exercise 3: cache hits
    h.contains(printed, "[Cache MISS]", "a cold key was executed")
    h.contains(printed, "[Cache HIT]", "a warm key came from the cache")
    h.equal(printed.count("[Cache HIT]"), 2, "both repeats were served from the cache")

    # exercise 4: structured output
    h.contains(printed, "Validation SUCCESS", "the structured answer parsed")
    h.contains(printed, "Tool: FlightSearchTool", "the tool name came from the schema")
    h.contains(printed, "Token Saving:", "the structured output is compared by tokens")

    h.write_json("result.json", {"trimming_percent": saving})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (solution shells)", FILES).crash())
