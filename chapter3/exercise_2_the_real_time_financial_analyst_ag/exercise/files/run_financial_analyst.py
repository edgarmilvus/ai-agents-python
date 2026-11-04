"""Harness for exercise 2: a stock-price tool over the mock financial API."""
import contextlib
import io
import json
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

CHAPTER = ROOT / "chapter3"
SETUP = CHAPTER / "necessary_setup_code_block/example/files" / "01_mock_services.py"


def compose(solution: pathlib.Path):
    source = SETUP.read_text() + "\n\n" + solution.read_text()
    namespace = {"__name__": "__main__"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source, str(solution), "exec"), namespace)
    return namespace


def main():
    h = Harness("exercise 2 (financial analyst)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        ns = compose(FILES / "01_financial_analyst_agent.py")
        quote = ns["get_stock_price"]("GOOGL")
        h.contains(quote, "155.20", "the GOOGL price comes from the mock API")
        h.contains(quote, "last updated", "the answer carries a timestamp")
        h.contains(ns["get_stock_price"]("msft"), "420.00",
                   "a lower-case ticker is upper-cased before the lookup")
        missing = ns["get_stock_price"]("NOPE")
        h.contains(missing, "API ERROR", "an unknown ticker is reported as an API error")
        h.contains(missing, "NOPE", "the error names the ticker it could not find")
        h.check("$nan" not in quote.lower(), "the price is formatted, not missing")

        h.write_json("result.json", {
            "googl": quote,
            "unknown": missing,
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (financial analyst)", FILES).crash())
