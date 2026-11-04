"""Harness for the ReAct agent: two tools, three scripted decisions.

The loop, the prompt and the tools are the listing's own. The harness scripts the
model, then checks that both tools ran and that the final answer is the executor's.
"""
import contextlib
import importlib.util
import io
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

RESPONSES = [
    "Thought: I need the price first.\nAction: get_stock_price\nAction Input: TSLA",
    'Thought: Now the momentum.\nAction: calculate_momentum_score\n'
    'Action Input: {"price": 185.50, "historical_avg": 175.00}',
    "Thought: I know the answer.\nFinal Answer: TSLA is at $185.50 with a momentum score "
    "of 6.0, so Buy.",
]


def main():
    h = Harness("example 2 (ReAct agent)", FILES)
    langchain_openai.ChatOpenAI = lambda **kwargs: FakeListChatModel(responses=RESPONSES)

    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        spec = importlib.util.spec_from_file_location("react_agent", str(FILES / "01_react_agent.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    printed = log.getvalue()

    h.contains(printed, "[TOOL CALLED] Fetching price for: TSLA", "the price tool ran")
    h.contains(printed, "[TOOL CALLED] Calculating momentum score", "the momentum tool ran")
    h.contains(printed, "Strong positive momentum", "the momentum result reached the loop")
    h.contains(module.result["output"], "Buy", "the final answer is the recommendation")

    h.contains(module.REACT_PROMPT_TEMPLATE, "{tool_names}", "the prompt lists the tool names")
    h.contains(module.REACT_PROMPT_TEMPLATE, "{agent_scratchpad}",
               "the prompt carries the ReAct scratchpad")
    h.equal(module.calculate_momentum_score.run(
        '{"price": 185.5, "historical_avg": 175.0}').count("score"), 1,
        "the momentum tool answers a JSON string")
    h.contains(module.calculate_momentum_score.run("not json"), "Error",
               "the momentum tool rejects malformed input")

    h.write_json("run.json", {
        "answer": module.result["output"],
        "tools_called": ["get_stock_price", "calculate_momentum_score"],
        "model": module.MODEL,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (ReAct agent)", FILES).crash())
