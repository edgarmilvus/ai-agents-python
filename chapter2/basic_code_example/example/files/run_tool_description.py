"""Harness for the tool-description snippet.

The listing is nine lines and does no work: what it demonstrates is the text a
model reads to decide whether to call a tool. So that text is the thing asserted.
"""
import json
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 1b (tool description)", FILES)
    module = load_listing(FILES / "02_tool_description.py", "tool_description")
    tool = module.get_current_stock_price

    h.equal(tool.name, "get_current_stock_price", "the tool is registered under its name")
    h.contains(tool.description, "real-time closing price", "the description states what it returns")
    h.contains(tool.description, "MUST be used", "the description states when to use it")
    h.contains(tool.description, "Do not guess", "the description forbids the model's alternative")
    h.check("GOOG" in tool.description and "AAPL" in tool.description,
            "the description carries examples of valid input")

    schema = json.dumps(tool.tool_call_schema.model_json_schema())
    h.contains(schema, "ticker", "the argument appears in the schema the model receives")
    h.equal(tool.invoke({"ticker": "goog"}).split(":")[0], "GOOG",
            "the tool upper-cases the ticker it was given")

    h.write_json("description.json", {
        "name": tool.name,
        "description": tool.description,
        "schema": tool.tool_call_schema.model_json_schema(),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1b (tool description)", FILES).crash())
