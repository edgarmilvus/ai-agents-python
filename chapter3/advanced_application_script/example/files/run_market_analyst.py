"""Harness for the market analyst: two tools, a scripted model, a real file.

The listing builds a client and calls two tools, one of which writes to disk. The
harness scripts the model's three JSON actions, runs the listing from its own
`output/` folder and checks both the answer and the file it produced.
"""
import contextlib
import importlib.util
import io
import json
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

# Imported before the filter: langchain installs its own warning filters on first
# import, and the harness log must stay free of site-packages paths.
warnings.simplefilter("ignore")

ACTIONS = [
    '{"action": "fetch_stock_price", "action_input": {"ticker": "MSFT"}}',
    '{"action": "log_market_data", "action_input": {"ticker": "MSFT", "price": 420.15, "volume": 1500000}}',
    '{"action": "Final Answer", "action_input": "MSFT is at 420.15 on volume 1500000, logged."}',
]


def main():
    h = Harness("example 4 (market analyst)", FILES)
    langchain_openai.ChatOpenAI = lambda **kwargs: FakeListChatModel(responses=ACTIONS)

    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        # The listing appends to its history file, so each run starts from empty.
        stale = output / "market_history.json"
        if stale.exists():
            stale.unlink()
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            spec = importlib.util.spec_from_file_location(
                "market_analyst", str(FILES / "01_market_analyst.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        printed = log.getvalue()

        h.contains(module.result["output"], "420.15", "the final answer quotes the price")
        h.contains(printed, "[TOOL CALL] Fetching data for MSFT", "the price tool ran")
        h.contains(printed, "[TOOL CALL] Logging data for MSFT", "the logging tool ran")

        history = json.loads(pathlib.Path("market_history.json").read_text())
        h.equal(len(history), 1, "one record was written to the history file")
        h.equal(history[0]["ticker"], "MSFT", "the record carries the ticker")
        h.equal(history[0]["price"], 420.15, "the record carries the price")
        h.check(history[0]["timestamp"], "the record carries a timestamp")

        h.contains(module.fetch_stock_price("NOPE"), "not found",
                   "an unknown ticker is reported, not invented")
        h.equal(json.loads(module.fetch_stock_price("MSFT"))["ticker"], "MSFT",
                "the price tool answers in JSON")

        h.write_json("run.json", {
            "answer": module.result["output"],
            "history": history,
            "model": module.MODEL,
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 4 (market analyst)", FILES).crash())
