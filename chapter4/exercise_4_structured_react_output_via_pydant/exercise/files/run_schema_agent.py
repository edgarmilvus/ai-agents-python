"""Harness for exercise 4: a Pydantic schema in front of the final answer."""
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
    h = Harness("exercise 4 (schema validation)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "02_schema_agent.py", "schema_agent")
    printed = log.getvalue()

    h.contains(printed, "Pydantic Validation Successful", "the mock answer validates")
    h.contains(printed, "confidence_score", "the validated output exposes the confidence")
    h.contains(printed, "tools_used", "the validated output counts the tools")

    result = module.generate_structured_final_answer("A topic", 2)
    h.equal(result["tools_used"], 2, "the tool count is carried into the schema")
    h.check(isinstance(result["key_findings"], list) and result["key_findings"],
            "the findings are a non-empty list")
    h.check(0 <= result["confidence_score"] <= 100, "the confidence is a percentage")

    invalid = dict(result, confidence_score=150)
    try:
        module.ResearchSummary(**invalid)
        h.check(False, "an out-of-range confidence must be rejected")
    except Exception:
        h.check(True, "the schema rejects an out-of-range confidence")

    h.write_json("result.json", {"validated": result})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (schema validation)", FILES).crash())
