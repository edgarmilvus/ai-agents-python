#!/usr/bin/env python3
"""Assemble the chapter's worked example from the four exercise solutions.

The chapter publishes the four solutions as separate programs and then the same
four, unchanged, in one file that also runs them. Keeping two hand-maintained
copies is how one of them goes stale, so the combined file is generated from the
four listings:

    python3 tools/build_chapter1_demo.py

The output is written to
chapter1/worked_example_the_whole_chapter_in_one_scrip/example/files/01_all_exercises_demo.py
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHAPTER = ROOT / "chapter1"

SOLUTIONS = [
    "exercise_1_simulating_the_ooda_loop/exercise/files/01_ooda_resource_collector.py",
    "exercise_2_implementing_rudimentary_episodic/exercise/files/01_episodic_memory_task_agent.py",
    "exercise_3_rule_based_tool_routing_and_execut/exercise/files/01_rule_based_tool_router.py",
    "exercise_4_interactive_challenge_introducing/exercise/files/01_planning_layer_rag.py",
]

TARGET = (
    "worked_example_the_whole_chapter_in_one_scrip/example/files/"
    "01_all_exercises_demo.py"
)

HEADER = [
    "import json",
    "import random",
    "import re",
    "",
    "# Chapter 1 - the whole chapter in one script.",
    "# Each exercise keeps the functions its own listing defines; the",
    "# __main__ block at the bottom runs all four in sequence.",
    "",
]

DEMO = '''
# --- Execution Demonstration ---

if __name__ == '__main__':
    
    # Exercise 1 Execution
    print("===================================================")
    print("EXERCISE 1: OODA Loop Agent Simulation")
    run_resource_agent()
    print("===================================================\\n")
    
    # Exercise 2 Execution
    print("===================================================")
    print("EXERCISE 2: State-Aware Task Agent (Memory)")
    # Note: Execution will loop and review if a task fails.
    run_task_agent()
    print("===================================================\\n")

    # Exercise 3 Execution
    print("===================================================")
    print("EXERCISE 3: Rule-Based Tool Router")
    run_tool_router_agent("I need to calculate 5 times 12")
    run_tool_router_agent("What is the weather in London?")
    run_tool_router_agent("Retrieve user data from the database.")
    run_tool_router_agent("Tell me a joke.") # Should fail to route
    print("===================================================\\n")

    # Exercise 4 Execution
    print("===================================================")
    print("EXERCISE 4: Planning Layer for RAG (Interactive Challenge)")
    
    # Case A: Simple query (no RAG needed)
    run_planning_agent("What is the capital of France?")
    
    # Case B: Complex query (RAG needed)
    run_planning_agent("What is the history of the early development of Python's GIL?")
    
    print("===================================================")
'''


def strip_imports(lines: list[str]) -> list[str]:
    """Drop the module-level imports each solution carries for itself."""
    while lines and (lines[0].startswith("import ") or lines[0].startswith("from ")):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def strip_main(lines: list[str]) -> list[str]:
    """Drop the trailing __main__ block; the demo owns the only entry point."""
    for index, line in enumerate(lines):
        if re.match(r"^if __name__ == ['\"]__main__['\"]:", line):
            return lines[:index]
    return lines


def body(relative: str) -> str:
    lines = (CHAPTER / relative).read_text().splitlines()
    lines = strip_main(strip_imports(lines))
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> None:
    text = "\n".join(HEADER) + "\n"
    for solution in SOLUTIONS:
        text += "\n" + body(solution)
    text += DEMO
    target = CHAPTER / TARGET
    target.write_text(text)
    lines = target.read_text().splitlines()
    print(f"wrote {target.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
