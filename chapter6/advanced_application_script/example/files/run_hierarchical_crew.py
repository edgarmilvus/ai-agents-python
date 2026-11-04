"""Harness for the CrewAI manager-worker crew.

The crew is hierarchical, so the manager is named by `manager_agent` and is not
part of the agents list; the harness checks that shape as well as the output.
"""
import contextlib
import io
import os
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import crewai  # noqa: E402
from crewai.llms.base_llm import BaseLLM  # noqa: E402

warnings.simplefilter("ignore")

BRIEF = ("STRATEGIC BRIEF: AuraFlow is a high threat. Cut the Growth tier price "
         "by 15% and launch a migration campaign for incumbent customers.")
CALLS = 0


class ScriptedLLM(BaseLLM):
    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        global CALLS
        CALLS += 1
        return BRIEF


def scripted_llm(**kwargs):
    scripted_llm.kwargs = kwargs
    return ScriptedLLM(model=str(kwargs.get("model", "scripted")))


def main():
    h = Harness("example 2 (hierarchical crew)", FILES)
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    crewai.LLM = scripted_llm

    module = load_listing(FILES / "01_hierarchical_crew.py", "hierarchical_crew")

    h.contains(str(module.result), "STRATEGIC BRIEF", "the manager returns the brief")
    h.check(CALLS >= 1, "the crew consulted the model")
    h.equal(module.competitive_crew.process.value, "hierarchical", "the crew is hierarchical")
    h.equal(len(module.competitive_crew.agents), 2, "only the two workers are listed as agents")
    h.check(module.competitive_crew.manager_agent is not None, "the manager is named separately")
    h.equal(module.competitive_crew.manager_agent.role, "Strategy Manager",
            "the manager is the strategy agent")

    pricing = module.research_tool.run("pricing tiers")
    h.contains(pricing, "$29", "the search tool returns pricing data")
    h.contains(module.research_tool.run("marketing messaging"), "CRM that thinks ahead",
               "the search tool returns marketing data")

    kwargs = scripted_llm.kwargs
    h.contains(str(kwargs.get("model")), module.MODEL_NAME, "the model comes from the environment")

    h.write_json("result.json", {"brief": str(module.result), "calls": CALLS,
                                 "agents": [a.role for a in module.competitive_crew.agents]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (hierarchical crew)", FILES).crash())
