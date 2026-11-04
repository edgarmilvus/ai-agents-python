"""agent-audit: the twelve failures of an agent system, checked in your source.

    agent-audit .                  # walk the current tree
    agent-audit src --exclude tests
    agent-audit --list             # the rules, with the chapter that explains each

Exit code 1 when anything is found, so it can sit in CI.
"""
from __future__ import annotations

import argparse
import fnmatch
import pathlib
import sys

from .rules import RULES, RULE_BY_ID, audit_source

DEFAULT_EXCLUDES = (".venv", "venv", "node_modules", "__pycache__", ".git",
                    "site-packages", "output", "build", "dist")


def walk(root: pathlib.Path, excludes):
    for path in sorted(root.rglob("*.py")):
        parts = set(path.parts)
        if parts & set(DEFAULT_EXCLUDES):
            continue
        if any(fnmatch.fnmatch(str(path), pat) or fnmatch.fnmatch(path.name, pat)
               for pat in excludes):
            continue
        yield path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="agent-audit", description=__doc__)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--exclude", action="append", default=[],
                    help="glob to skip, repeatable (e.g. --exclude 'run_*.py')")
    ap.add_argument("--only", action="append", default=None,
                    help="run only these rule ids, repeatable")
    ap.add_argument("--list", action="store_true", help="print the rules and exit")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if args.list:
        for rule in sorted(RULES, key=lambda r: r.chapter):
            print(f"{rule.id:<18} ch{rule.chapter:<3} {rule.title}")
        return 0

    root = pathlib.Path(args.path)
    if not root.exists():
        print(f"no such path: {root}", file=sys.stderr)
        return 2

    findings = []
    files = 0
    for path in walk(root, args.exclude):
        files += 1
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(audit_source(path, source, args.only))

    if args.json:
        import json
        print(json.dumps({"files": files, "findings": findings}, indent=2))
    else:
        for f in sorted(findings, key=lambda x: (x["path"], x["line"])):
            print(f"{f['path']}:{f['line']}  {f['rule']}  (ch{f['chapter']})")
            print(f"    {f['message']}")
        print()
        print(f"{files} files · {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
