"""Harness for exercise 2: the structured output package.

One valid JSON document, one that is not JSON, and one that is JSON but missing a
required field. The two rejected cases are the ones a real model produces.
"""
import json
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

VALID = {
    "rationale": "Uses a loop for clarity.",
    "function_code": {"code_string": "def double(n):\n    return n * 2", "language": "python"},
    "test_code": {"code_string": "import unittest\nclass T(unittest.TestCase):\n    pass",
                  "language": "python"},
}


def main():
    h = Harness("exercise 2 (structured output)", FILES)
    module = load_listing(FILES / "01_structured_output.py", "structured_output")

    package = module.parse_agent_output(json.dumps(VALID))
    h.equal(package.rationale, VALID["rationale"], "the rationale survived parsing")
    h.equal(package.function_code.code_string, VALID["function_code"]["code_string"],
            "the function code survived parsing")
    h.equal(package.test_code.language, "python", "the language defaults to python")

    h.equal(module.parse_agent_output("this is not json"), None,
            "a non-JSON answer is rejected, not raised")

    missing = json.dumps({"rationale": "x", "function_code": {"code_string": "pass"}})
    h.equal(module.parse_agent_output(missing), None,
            "a package missing test_code is rejected")

    solution, tests = module.prepare_files_for_execution(package)
    try:
        h.check(os.path.exists(solution) and os.path.exists(tests),
                "both temp files were written")
        h.contains(pathlib.Path(solution).read_text(), "def double", "the solution file holds the code")
        h.contains(pathlib.Path(tests).read_text(), "unittest", "the test file holds the tests")
    finally:
        for path in (solution, tests):
            if os.path.exists(path):
                os.remove(path)

    h.write_json("result.json", {"parsed": True, "rejected": 2})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (structured output)", FILES).crash())
