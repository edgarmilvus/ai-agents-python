"""Harness for the strategic analyst: RAG context, one tool, a forced plan.

The model is scripted, but the RAG retrieval, the prompt and the tool call are the
listing's own: the harness checks that the first decision really reached the tool
and that the second answer is what the executor returned.
"""
import contextlib
import io
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

# The listings use the deprecated-in-name classic APIs on purpose; the
# warning would otherwise put a site-packages path in the harness log.

import langchain_openai  # noqa: E402
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

# Import this before installing the filter: langchain resets the warning
# filters when it first loads, and the log would otherwise carry a
# site-packages path with the username in it.
import langchain_classic.memory  # noqa: E402,F401

warnings.simplefilter("ignore")

RESPONSES = [
    "Thought: I need external market data.\n"
    "Action: external_market_data_search\n"
    "Action Input: recipe planner market saturation competitors",
    "Thought: I now know the final answer\n"
    "Final Answer: Price at $19.99, add grocery delivery integration to close the competitor gap.",
]

CLIENT_KWARGS = []


def scripted_client(**kwargs):
    CLIENT_KWARGS.append(kwargs)
    return FakeListChatModel(responses=RESPONSES)


def main():
    h = Harness("example 2 (strategic analyst)", FILES)
    langchain_openai.ChatOpenAI = scripted_client

    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_strategic_analyst.py", "strategic_analyst")
    printed = log.getvalue()

    h.equal(module.result["output"],
            "Price at $19.99, add grocery delivery integration to close the competitor gap.",
            "the executor returns the final answer")
    h.contains(printed, "market_saturation",
               "the tool's JSON reached the agent as an Observation")
    h.contains(printed, "7/10", "the observation carries the saturation the tool returned")
    h.contains(module.full_prompt_with_rag, "Q4 2023",
               "the RAG context is injected before execution")
    h.contains(module.SYSTEM_PROMPT, "RAG Retrieval", "the prompt states the sequence")
    h.contains(module.SYSTEM_PROMPT, "Final Plan", "the prompt states the last stage")
    h.contains(str(module.memory.load_memory_variables({})), "RAG CONTEXT",
               "the run is recorded in short-term memory")

    kwargs = CLIENT_KWARGS[0]
    h.equal(kwargs.get("model"), module.MODEL, "the model comes from the environment")
    h.equal(kwargs.get("base_url"), module.BASE_URL, "the base URL comes from the environment")
    h.equal(kwargs.get("temperature"), 0.1, "the planner keeps a low temperature")

    h.write_json("run.json", {
        "rag_context": module.rag_context,
        "observation_contains_saturation": "market_saturation" in printed,
        "final": module.result["output"],
        "model": module.MODEL,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (strategic analyst)", FILES).crash())
