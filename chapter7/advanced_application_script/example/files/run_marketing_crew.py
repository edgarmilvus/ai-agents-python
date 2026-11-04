"""Harness for the collaborative marketing crew."""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402
from scripted_crew import CALLS, install  # noqa: E402


def main():
    h = Harness("example 2 (marketing crew)", FILES)
    install()
    module = load_listing(FILES / "01_marketing_crew.py", "marketing_crew")

    h.contains(str(module.campaign_result), "SCRIPTED OUTPUT", "the crew returns the model output")
    h.equal(len(module.project_crew.agents), 3, "three specialists")
    h.check(len(module.project_crew.tasks) >= 2, "the workflow has at least two tasks")
    h.check(any(a.allow_delegation for a in module.project_crew.agents),
            "one agent may delegate")

    tool = module.search_tool
    h.contains(tool.run("generative AI in medicine"), "paid deployments",
               "the search tool answers from its corpus")
    h.equal(tool.name, "web_search", "the tool is registered under its name")

    h.write_json("result.json", {"output": str(module.campaign_result), "calls": len(CALLS),
                                 "agents": [a.role for a in module.project_crew.agents]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (marketing crew)", FILES).crash())
