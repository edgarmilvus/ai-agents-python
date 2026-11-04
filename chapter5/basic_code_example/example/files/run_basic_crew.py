"""Harness for the basic CrewAI agent.

CrewAI needs a model to run a crew, so the harness substitutes its `LLM` class
with a scripted one: the agent, the task and the crew are the listing's own, and
`kickoff()` still goes through CrewAI's orchestration.
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

REPORT = (
    "# Serverless Computing: Executive Summary\n\n"
    "Serverless platforms now carry a large share of new workloads. "
    "FaaS removes capacity planning and bills per invocation."
)
CALLS = 0


class ScriptedLLM(BaseLLM):
    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        global CALLS
        CALLS += 1
        return REPORT


def scripted_llm(**kwargs):
    scripted_llm.kwargs = kwargs
    return ScriptedLLM(model=str(kwargs.get("model", "scripted")))


def main():
    h = Harness("example 1 (basic crew)", FILES)
    # The listings check that a key is configured before they run. No call is
    # made here, so a placeholder satisfies the check without a secret.
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    crewai.LLM = scripted_llm
    module = load_listing(FILES / "01_basic_research_agent.py", "basic_crew")

    text = str(module.result)
    h.contains(text, "Serverless", "the crew returns the model's report")
    h.equal(CALLS, 1, "one task, one model call")
    h.equal(module.research_analyst_agent.role, "Senior Market Research Analyst",
            "the agent keeps the role from the listing")
    h.equal(module.research_analyst_agent.allow_delegation, False,
            "the single agent does not delegate")
    h.contains(module.research_task.description, "Serverless Computing",
            "the task carries the topic")
    h.contains(module.research_task.expected_output, "three-paragraph",
            "the task states the expected structure")

    kwargs = scripted_llm.kwargs
    h.contains(str(kwargs.get("model")), module.MODEL, "the model comes from the environment")
    h.equal(kwargs.get("base_url"), module.BASE_URL, "the base URL comes from the environment")

    h.write_json("result.json", {"report": text, "calls": CALLS, "model": module.MODEL})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (basic crew)", FILES).crash())
