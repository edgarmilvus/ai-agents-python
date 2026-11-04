"""Harness for exercise 2: a structured, date-constrained report.

The schema is the contract, so the harness validates against it directly and
checks that the cutoff date travels from the prompt into the validated object.
"""
import contextlib
import io
import json
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 2 (dynamic structured agent)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "02_exercise_2_dynamic_structured_agent.py", "dynamic_agent")
        report = module.run_dynamic_research_query("Quantum computing", "2021-01-01")
    printed = log.getvalue()

    h.contains(module.create_dynamic_prompt("X", "2020-01-01"), "2020-01-01",
               "the prompt carries the cutoff date")
    parsed = json.loads(report)
    h.equal(parsed["cutoff_date_used"], "2021-01-01", "the validated report keeps the date")
    h.check(isinstance(parsed["key_insights"], list) and len(parsed["key_insights"]) >= 3,
            "the report carries at least three insights")
    h.check(parsed["source_count"] > 0, "the report counts its sources")
    h.contains(parsed["query"], "Quantum", "the report echoes the topic")

    h.check("ValidationError" not in printed, "no invalid payload was produced")

    bad = dict(parsed, source_count="many")
    try:
        module.ResearchReport(**bad)
        h.check(False, "a non-numeric source count must be rejected")
    except Exception:
        h.check(True, "the schema rejects a non-numeric source count")

    h.write_json("result.json", parsed)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (dynamic structured agent)", FILES).crash())
