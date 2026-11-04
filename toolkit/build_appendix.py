#!/usr/bin/env python3
"""Render the book's appendix from the rules, so prose and checks cannot drift.

    python toolkit/build_appendix.py            # print the section
    python toolkit/build_appendix.py --write    # replace it in the manuscript

The section uses indented code blocks, not fenced ones: the book's extractor
treats a fence under an "appendix" heading as a listing it must be able to run,
and these are illustrations, not listings.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from agent_audit.rules import RULES  # noqa: E402

BEGIN = "<!-- BEGIN generated from toolkit/agent_audit/rules.py -->"
END = "<!-- END generated from toolkit/agent_audit/rules.py -->"

HEADER = """# Appendix — Auditing your own agent {-}

The book describes twelve ways an agent system fails. This appendix turns them into
a check you can run on your own code: `agent-audit` reads a Python tree, reports each
failure with the line and the chapter that explains it, and exits non-zero so it can
sit in a pipeline.

The check lives in the repository, under `toolkit/`. It is deliberately small — no
plugins, no configuration file, no dependency outside the standard library — because
a rule you cannot read is a rule you cannot trust.

## Install and run

    cd python-ai-agents
    python -m pip install ./toolkit
    agent-audit .                 # exit code 1 when something is found
    agent-audit . --list          # the twelve rules and their chapters
    agent-audit . --json          # machine-readable, for CI

A report looks like this:

    src/agent.py:88   budget            (ch17)
        A loop calls the model with nothing that bounds calls, tokens or time.
    src/tools.py:41   untyped-tool      (ch3)
        A tool is exposed to the model without annotations or with **kwargs.

    two findings in 41 files

Each rule is one failure, one chapter, and one fix. The chapter is the explanation;
the check is the enforcement.

## What it does not do

It does not judge your prompts. Every rule here is about structure — a bound, an
exit, a type, a trace — and structure is exactly what a static check can see. Whether
the prompt is any good is answered by running it against a real model, which is the
live table at the beginning of the book: twenty-one listings, a few cents, and it is
the only part that costs money.

## The twelve rules
"""

FOOTER = """
## How the checks are trusted

Three fixtures, one claim each:

    toolkit/tests/fixtures/trap/     twelve files, one per rule: every rule must fire
    toolkit/tests/fixtures/clean/    a correct agent: nothing may fire
    this repository                  verified by 133 harnesses: zero findings

The third is the one that keeps the others honest. If the audit accuses code that a
thousand assertions have already accepted, the rule is wrong — and it gets fixed or
removed, not excused. Run the suite with:

    cd toolkit && python -m unittest discover -s tests

One rule is deliberately soft. `retry-logical` cannot see what an exception means, so
it only fires on a retry loop that swallows a generic failure; it will not tell you
that a 404 was retried, only that nothing in the loop distinguishes it from a timeout.
Treat it as a prompt to read the handler, not as a verdict.
"""


def paragraph(text: str) -> str:
    return " ".join(text.split())


def render() -> str:
    parts = [HEADER.strip(), ""]
    for rule in sorted(RULES, key=lambda r: r.chapter):
        parts.append(f"### {rule.title} — chapter {rule.chapter}")
        parts.append("")
        parts.append(paragraph(f"**{rule.message}**"))
        parts.append("")
        parts.append("What it looks like:")
        parts.append("")
        parts.extend("    " + line for line in rule.wrong.splitlines())
        parts.append("")
        parts.append("What to write instead:")
        parts.append("")
        parts.extend("    " + line for line in rule.right.splitlines())
        parts.append("")
    parts.append(FOOTER.strip())
    return "\n".join(parts) + "\n"


def replace_in_book(book: pathlib.Path, section: str) -> bool:
    text = book.read_text()
    block = f"{BEGIN}\n\n{section}\n{END}"
    if BEGIN in text and END in text:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), block, text, flags=re.S)
        changed = new != text
        book.write_text(new)
        return changed
    raise SystemExit(f"markers not found in {book}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="replace the section in the book")
    ap.add_argument("--book", default="Python_AI_Autonomous_Agents.md")
    ap.add_argument("--check", action="store_true", help="fail if the book is out of date")
    args = ap.parse_args()

    section = render()
    if args.check:
        text = pathlib.Path(args.book).read_text()
        current = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), text, re.S)
        same = current and current.group(1).strip() == section.strip()
        print("appendix is up to date" if same else "appendix differs from the rules")
        return 0 if same else 1
    if args.write:
        changed = replace_in_book(pathlib.Path(args.book), section)
        print("appendix rewritten" if changed else "appendix already current")
        return 0
    sys.stdout.write(section)
    return 0


if __name__ == "__main__":
    sys.exit(main())
