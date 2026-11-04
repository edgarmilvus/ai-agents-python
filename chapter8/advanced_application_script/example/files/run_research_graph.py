"""Harness for the advanced research graph: verify, refine, search again.

The graph is deterministic except for the model, so the harness scripts the three
answers the verifier and the refiner ask for.
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

import langchain_openai  # noqa: E402
import langchain_classic.memory  # noqa: E402,F401
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

warnings.simplefilter("ignore")

RESPONSES = ["YES_REFINE", "Apollo 11 scientific instruments list", "NO_COMPLETE"]


def main():
    h = Harness("example 2 (research graph)", FILES)
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    langchain_openai.ChatOpenAI = lambda **kwargs: FakeListChatModel(responses=RESPONSES)

    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "research_graph", str(FILES / "01_research_graph.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    printed = log.getvalue()

    h.equal(module.final_state["iteration_count"], 2, "the cycle ran once")
    h.equal(module.final_state["query"], "Apollo 11 scientific instruments list",
            "the refiner replaced the query")
    h.contains(printed, "Needs refinement", "the verifier rejected the first result")
    h.contains(printed, "satisfactory", "the verifier accepted the second")
    h.contains(printed, "TOOL: Searching", "the researcher node ran")
    h.check(printed.count("TOOL: Searching") == 2, "the tool ran once per iteration")
    h.check(module.final_state["iteration_count"] <= module.final_state["max_iterations"],
            "the loop respects its own limit")

    h.write_json("result.json", {
        "iterations": module.final_state["iteration_count"],
        "refined_query": module.final_state["query"],
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (research graph)", FILES).crash())
