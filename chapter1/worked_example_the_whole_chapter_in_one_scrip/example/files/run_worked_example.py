"""Harness for the chapter's worked example.

The demo is generated from the four solution listings, so two things are
checked: that it still contains each listing unchanged, and that running it
reaches the end of all four exercises.
"""
import pathlib
import re
import subprocess
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
CHAPTER = ROOT / "chapter1"
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

DEMO = FILES / "01_all_exercises_demo.py"
SOLUTIONS = [
    "exercise_1_simulating_the_ooda_loop/exercise/files/01_ooda_resource_collector.py",
    "exercise_2_implementing_rudimentary_episodic/exercise/files/01_episodic_memory_task_agent.py",
    "exercise_3_rule_based_tool_routing_and_execut/exercise/files/01_rule_based_tool_router.py",
    "exercise_4_interactive_challenge_introducing/exercise/files/01_planning_layer_rag.py",
]


def body(path):
    lines = path.read_text().splitlines()
    while lines and (lines[0].startswith("import ") or lines[0].startswith("from ")):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    for index, line in enumerate(lines):
        if re.match(r"^if __name__ == ['\"]__main__['\"]:", line):
            lines = lines[:index]
            break
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def contains_run(haystack, needle):
    if not needle:
        return False
    for start in range(len(haystack) - len(needle) + 1):
        if haystack[start:start + len(needle)] == needle:
            return True
    return False


def main():
    h = Harness("worked example (whole chapter)", FILES)

    demo_lines = body(DEMO)
    for solution in SOLUTIONS:
        h.check(contains_run(demo_lines, body(CHAPTER / solution)),
                f"the demo carries {pathlib.Path(solution).name} unchanged")

    completed = subprocess.run(
        [sys.executable, str(DEMO)],
        capture_output=True,
        text=True,
        cwd=str(FILES),
    )
    log = completed.stdout + completed.stderr

    h.equal(completed.returncode, 0, "the demo exits cleanly")
    for number in range(1, 5):
        h.contains(log, f"EXERCISE {number}", f"exercise {number} ran")
    h.contains(log, "All Tasks Completed Successfully", "the memory agent finished its tasks")
    h.contains(log, "Calculation Tool Result: The result of 5 * 12 is 60.",
               "the router turned the word 'times' into an operation")
    h.contains(log, "Weather Tool Result: Current weather in London: 15°C and cloudy.",
               "the weather tool answered")
    h.contains(log, "Direct Answer Result", "the simple query skipped retrieval")
    h.contains(log, "RAG Result", "the complex query used retrieval")
    h.check("Traceback" not in log, "no exercise crashed")

    h.write_text("demo.log", log)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("worked example (whole chapter)", FILES).crash())
