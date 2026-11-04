"""Harness for the four exercise scripts.

The block defines one client, one model and the four functions the exercises ask
for, with every demo commented out. The harness supplies the client and one model
per `ChatOpenAI(...)` call, then drives each exercise: a traced extraction, a tool
that has to reject "150 units", a cost comparison, and two research policies.
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
from fake_langsmith import FakeClient  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402
import langchain_openai  # noqa: E402
import langsmith  # noqa: E402


def call(name, **args):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call-{name}"}])


def main():
    h = Harness("example 3 (exercise scripts)", FILES)
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    client = FakeClient()
    langsmith.Client = lambda *args, **kwargs: client

    # One model per ChatOpenAI(...) call, in the order the script makes them.
    models = [
        # 1. the module-level llm: one extraction answer, then a bad tool call
        ScriptedToolChat(responses=[
            AIMessage(content='{"percentage": 15.5, "base_amount": 12500.0}'),
            call("inventory_checker", amount="150 units"),
            AIMessage(content="I could not confirm the stock."),
        ]),
        ScriptedToolChat(responses=[call("inventory_checker", amount="350"),
                                    AIMessage(content="350 units are available.")]),
        ScriptedToolChat(responses=[call("inventory_checker", amount="350"),
                                    AIMessage(content="350 units are available.")]),
        ScriptedToolChat(responses=[call("search_tool", query="current year"),
                                    call("calculator_tool", expression="sqrt(144)+2024"),
                                    AIMessage(content="Search first, then calculation.")]),
        ScriptedToolChat(responses=[call("calculator_tool", expression="sqrt(144)+2024"),
                                    call("search_tool", query="current year"),
                                    AIMessage(content="Calculation first, then search.")]),
    ]
    langchain_openai.ChatOpenAI = lambda **kwargs: models.pop(0)

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        ns = runpy.run_path(str(FILES / "01_exercise_scripts.py"), run_name="__main__")

    # --- exercise 1: the root run is opened through the client
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        result = ns["run_financial_analysis"]("Calculate 15.5% of $12,500 for tax purposes.")
    h.contains(result, "15.5", "the extraction returned the model's answer")
    h.equal(len(client.created_runs), 1, "one root run was opened")
    h.equal(client.created_runs[0].tags, ["finance", "extraction"], "the tags reached the client")
    h.equal(client.created_runs[0].metadata["environment"], "production",
            "the metadata reached the client")
    h.contains(client.created_runs[0].outputs["extracted_data"], "15.5",
               "the run recorded the extracted answer")

    # --- exercise 2: the tool has to reject the unit suffix
    tool = ns["inventory_checker"]
    h.contains(tool.invoke("150"), "Only 150 units", "a bare number passes")
    try:
        tool.invoke("150 units")
    except ValueError as exc:
        h.contains(str(exc), "not a valid positive integer", "the unit suffix is rejected")
    else:
        h.check(False, "the tool should reject '150 units'")

    executor = ns["setup_inventory_agent"]()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            executor.invoke({"input": "I need to check the inventory for 150 items."})
    except ValueError as exc:
        h.contains(str(exc), "not a valid positive integer",
                   "the agent run fails for the reason the trace shows")
    else:
        h.check(False, "the failing tool call should reach the caller")

    # --- exercise 3: two configurations, same query
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        ns["run_cost_comparison"](executor, "I need to confirm the stock for 350 items.")
    printed_cost = log.getvalue()
    h.contains(printed_cost, "Configuration 1", "the premium configuration ran")
    h.contains(printed_cost, "Configuration 2", "the economy configuration ran")

    # --- exercise 4: two policies
    policy_a = ns["setup_research_agent"](0.1, "Policy A - Search First")
    with contextlib.redirect_stdout(io.StringIO()):
        answer_a = policy_a.invoke({"input": "What is the square root of 144 plus the current year?"},
                                   config={"tags": ["policy-A"]})
    policy_b = ns["setup_research_agent"](0.9, "Policy B - Calculator First")
    with contextlib.redirect_stdout(io.StringIO()):
        answer_b = policy_b.invoke({"input": "What is the square root of 144 plus the current year?"},
                                   config={"tags": ["policy-B"]})
    h.equal([tool.name for tool in policy_a.tools], ["search_tool", "calculator_tool"],
            "policy A keeps both tools")
    h.contains(answer_a["output"], "Search first", "policy A answered")
    h.contains(answer_b["output"], "Calculation first", "policy B answered")

    h.write_json("result.json", {"runs": len(client.created_runs)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise scripts)", FILES).crash())
