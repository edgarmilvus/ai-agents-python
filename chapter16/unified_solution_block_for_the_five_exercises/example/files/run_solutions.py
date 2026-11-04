"""Harness for the unified solution block.

The block runs all five exercises at import: a traced extraction, a failing tool
call, a cost comparison, two research policies and a dataset built from existing
runs. The harness supplies the client, the models and two completed runs, then
checks that each exercise reached its own conclusion.
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
from fake_langsmith import FakeClient, seed_run  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402
import langchain_openai  # noqa: E402
import langsmith  # noqa: E402


def call(name, **args):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call-{name}"}])


def main():
    h = Harness("example 4 (unified solutions)", FILES)
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    client = FakeClient()
    seed_run(client, "policy A run 1",
             {"input": "What is the square root of 144 plus the current year?"},
             {"output": "sqrt(144) is 12; the year is 2024, so 2036."})
    seed_run(client, "policy A run 2",
             {"input": "Who wrote the first compiler?"},
             {"output": "Grace Hopper's team wrote the first compiler."})
    langsmith.Client = lambda *args, **kwargs: client

    models = [
        ScriptedToolChat(responses=[AIMessage(content="unused")]),
        ScriptedToolChat(responses=[AIMessage(content='{"percentage": 15.5, "base_amount": 12500.0}')]),
        ScriptedToolChat(responses=[call("inventory_checker", amount="150 units"),
                                    AIMessage(content="Could not confirm.")]),
        ScriptedToolChat(responses=[call("inventory_checker", amount="350"),
                                    AIMessage(content="350 units are available.")]),
        ScriptedToolChat(responses=[call("inventory_checker", amount="350"),
                                    AIMessage(content="350 units are available.")]),
        ScriptedToolChat(responses=[call("search_tool", query="current year"),
                                    call("calculator_tool", expression="sqrt(144)+2024"),
                                    AIMessage(content="Policy A answered.")]),
        ScriptedToolChat(responses=[call("calculator_tool", expression="sqrt(144)+2024"),
                                    call("search_tool", query="current year"),
                                    AIMessage(content="Policy B answered.")]),
    ]
    langchain_openai.ChatOpenAI = lambda **kwargs: models.pop(0)

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_solutions.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Running Exercise 1: Custom Tracing and Metadata", "exercise 1 ran")
    h.contains(printed, "Trace completed. View run ID:", "the root run was closed")
    h.equal(len(client.created_runs), 1, "one root run reached the client")
    h.equal(client.created_runs[0].tags, ["finance", "extraction", "custom-trace"],
            "the tags reached the client")

    h.contains(printed, "Running Exercise 2: Debugging Tool Failure", "exercise 2 ran")
    h.contains(printed, "Agent execution failed as expected", "the bad tool input surfaced")

    h.contains(printed, "Running Configuration 1", "exercise 3 ran the premium configuration")
    h.contains(printed, "Running Configuration 2", "exercise 3 ran the economy configuration")

    h.contains(printed, "Running Exercise 4: Policy A", "exercise 4 ran policy A")
    h.contains(printed, "Running Exercise 4: Policy B", "exercise 4 ran policy B")

    h.contains(printed, "Successfully added 2 examples", "exercise 5 built the dataset")
    dataset = client.datasets["Research-Agent-Gold-Standard-V1"]
    h.equal(len(dataset.examples), 2, "both seeded runs became examples")
    h.equal(dataset.examples[0]["inputs"]["question"],
            "What is the square root of 144 plus the current year?",
            "the example keeps the run's input")

    h.write_json("result.json", {"examples": len(dataset.examples)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (unified solutions)", FILES).crash())
