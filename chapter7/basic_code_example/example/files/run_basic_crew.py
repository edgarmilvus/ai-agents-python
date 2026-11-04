"""Harness for the basic sequential crew."""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402
from scripted_crew import CALLS, install  # noqa: E402


def main():
    h = Harness("example 1 (sequential crew)", FILES)
    install()
    module = load_listing(FILES / "01_sequential_crew.py", "basic_crew")

    h.contains(str(module.result), "SCRIPTED OUTPUT", "the crew returns the model output")
    h.check(len(CALLS) >= 1, "the crew consulted the model")
    h.equal(len(module.project_crew.agents), 2, "two agents")
    h.equal(len(module.project_crew.tasks), 2, "two tasks")
    h.equal(module.project_crew.process.value, "sequential", "the process is sequential")
    h.equal(module.researcher.role, "Senior Research Analyst", "the researcher keeps its role")
    h.equal(module.writer.role, "Creative Content Strategist", "the writer keeps its role")
    h.contains(module.research_task.description, "Python", "the research task names the topic")
    h.check(module.writing_task.context or module.writing_task.description,
            "the writing task is defined")

    h.write_json("result.json", {"output": str(module.result), "calls": len(CALLS)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (sequential crew)", FILES).crash())
