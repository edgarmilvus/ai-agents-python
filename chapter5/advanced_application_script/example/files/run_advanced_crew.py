"""Harness for the advanced CrewAI agent.

The crew runs against a scripted model; the tool is exercised on its own, and the
brief the crew writes to disk is checked after the run.
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

from harness import Harness  # noqa: E402

import crewai  # noqa: E402
from crewai.llms.base_llm import BaseLLM  # noqa: E402

warnings.simplefilter("ignore")

BRIEF = (
    "# Executive Brief: Personalized Cancer Vaccines\n\n"
    "## 1. Market Overview and Current State\nThree platforms entered late-stage trials.\n\n"
    "## 2. Key Technological Innovations\n- Neoantigen selection\n- mRNA delivery\n\n"
    "## 3. Top 3 Companies/Research Groups\n- BioNTech\n- Moderna\n- Genentech\n\n"
    "## 4. Market Challenges\n- Manufacturing cost\n- Reimbursement"
)
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
    h = Harness("example 2 (advanced crew)", FILES)
    # The listings check that a key is configured before they run. No call is
    # made here, so a placeholder satisfies the check without a secret.
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    crewai.LLM = scripted_llm

    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    brief = output / "executive_brief.md"
    if brief.exists():
        brief.unlink()
    previous = os.getcwd()
    os.chdir(output)
    try:
        import importlib.util
        with contextlib.redirect_stdout(io.StringIO()):
            spec = importlib.util.spec_from_file_location(
                "advanced_crew", str(FILES / "01_advanced_application_script.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        h.equal(CALLS, 1, "one task, one model call")
        h.check(brief.exists(), "the crew wrote its brief to disk")
        h.contains(brief.read_text(), "Executive Brief", "the brief is the model's report")
        h.equal(module.market_analyst_agent.allow_delegation, False,
                "the single agent does not delegate")
        h.equal(module.research_crew.process.value, "sequential", "the crew runs sequentially")

        tool = module.internet_search_tool
        result = tool.run("serverless platforms")
        h.contains(result, "Corpus results", "the search tool answers")
        h.contains(result, "vendor lock-in", "the tool returns the curated finding")
        h.equal(tool.name, "market_search", "the tool is registered under its name")

        h.write_json("result.json", {"calls": CALLS, "brief_chars": len(BRIEF)})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (advanced crew)", FILES).crash())
