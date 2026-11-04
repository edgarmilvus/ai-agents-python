"""The acceptance test: the trap repo lights every rule, the book repo stays quiet."""
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from agent_audit.rules import RULES, audit_source  # noqa: E402


def audit(path, **kw):
    findings = []
    for file in sorted(pathlib.Path(path).rglob("*.py")):
        findings.extend(audit_source(file, file.read_text(), **kw))
    return findings


class TrapRepo(unittest.TestCase):
    def test_every_rule_fires(self):
        found = {f["rule"] for f in audit(HERE / "fixtures" / "trap")}
        expected = {r.id for r in RULES}
        self.assertEqual(expected - found, set(), "rules that never fired")
        self.assertEqual(len(found), len(expected))

    def test_clean_sample_is_silent(self):
        self.assertEqual(audit(HERE / "fixtures" / "clean"), [])


class BookRepo(unittest.TestCase):
    """The book's own code is verified by 133 harnesses: the audit must agree."""

    def test_no_findings(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        findings = []
        for file in root.rglob("*.py"):
            parts = set(file.parts)
            if parts & {"toolkit", "output", "__pycache__", ".venv"}:
                continue
            if file.name.startswith("run_"):
                continue          # harnesses are not the system under audit
            findings.extend(audit_source(file, file.read_text()))
        self.assertEqual(findings, [], f"{len(findings)} finding(s) on the book's code")


if __name__ == "__main__":
    unittest.main()
