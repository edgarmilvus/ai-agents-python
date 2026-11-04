"""Harness for the traced ReAct agent: two queries, two tools.

The listing binds two tools and lets a model route between them. The fake is given
the whole conversation — a search call, an answer, a calculation call, an answer —
so both runs exercise a different path through the same executor.
"""
import contextlib
import io
import os
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

from fake_agents import ScriptedToolChat  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402
import langchain_openai  # noqa: E402

SCRIPT = [
    AIMessage(content="", tool_calls=[{"name": "search_financial_news",
                                       "args": {"query": "Tesla stock"},
                                       "id": "call-1"}]),
    AIMessage(content="Tesla is up 5% after the battery factory news."),
    AIMessage(content="", tool_calls=[{"name": "calculate_simple_growth",
                                       "args": {"initial_value": 5000, "growth_rate": 12},
                                       "id": "call-2"}]),
    AIMessage(content="The projected value is $5600.00."),
]


def main():
    h = Harness("example 2 (traced agent)", FILES)
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    langchain_openai.ChatOpenAI = lambda **kwargs: ScriptedToolChat(responses=list(SCRIPT))

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        namespace = runpy.run_path(str(FILES / "01_traced_agent.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "--- TOOL CALL: Searching news for 'Tesla stock' ---",
               "the search tool ran on the first query")
    h.contains(printed, "--- TOOL CALL: Calculating growth: 5000",
               "the calculation tool ran on the second query")
    h.contains(namespace["result_1"]["output"], "up 5%",
               "the first answer came back through the executor")
    h.contains(namespace["result_2"]["output"], "5600",
               "the second answer came back through the executor")
    h.equal(len(namespace["tools"]), 2, "both tools are bound to the agent")
    h.equal(os.environ["LANGCHAIN_PROJECT"], "Financial Agent Observability Demo",
            "the project name is set for the trace")

    h.write_json("result.json", {"answer_1": namespace["result_1"]["output"],
                                 "answer_2": namespace["result_2"]["output"]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (traced agent)", FILES).crash())
