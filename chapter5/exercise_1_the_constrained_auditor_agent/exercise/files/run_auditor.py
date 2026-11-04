"""Harness for exercise 1: the constrained auditor.

The constraint lives in the role description and in the tool list, so the harness
checks both: the run refuses the external check, and the only tool available is
the internal one.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 1 (constrained auditor)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_exercise_1_auditor_agent.py", "auditor")

        answer = module.run_constrained_auditor(
            module.INTERNAL_AUDITOR_ROLE, module.CONSTRAINT_TEST_PROMPT,
            [module.File_Reader_Tool()])
    printed = log.getvalue()

    h.contains(module.INTERNAL_AUDITOR_ROLE, "PROHIBITED", "the role states the prohibition")
    h.contains(module.INTERNAL_AUDITOR_ROLE, "cannot perform the external check",
               "the role says what to do instead of searching")
    h.contains(module.CONSTRAINT_TEST_PROMPT, "CVE", "the test prompt asks for external data")
    h.contains(printed, "File_Reader_Tool", "the only tool in the list is the internal one")

    h.contains(answer, "cannot", "the auditor refuses the external check")
    h.contains(answer, "Internal Analysis", "it still analyses what it can from the snippet")
    h.contains(answer, "timeout", "the internal analysis finds the hardcoded timeout")
    h.contains(answer, "GoogleSearchTool", "the report names the tool it was denied")

    h.write_json("result.json", {"answer": answer[:500]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (constrained auditor)", FILES).crash())
