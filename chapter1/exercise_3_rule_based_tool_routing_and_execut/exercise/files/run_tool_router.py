"""Harness for exercise 3: routing a query to the right mock tool.

The interesting cases are the ones string matching gets wrong: an operator
written as a word, a city whose name contains the preposition, and an
expression that is not arithmetic at all.
"""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

QUERIES = [
    "I need to calculate 5 times 12",
    "What is the weather in London?",
    "What is the forecast in Berlin?",
    "Retrieve user data from the database.",
    "Tell me a joke.",
]
INJECTION = "__import__('os').system('echo pwned')"


def main():
    h = Harness("exercise 3 (tool router)", FILES)
    listing = load_listing(FILES / "01_rule_based_tool_router.py", "tool_router")

    tool, expression = listing.route_query(QUERIES[0])
    h.equal(tool, "calculate", "the word calculate routes to the calculator")
    h.equal(expression, "5 * 12", "the operator word is rewritten into an operator")
    h.equal(listing.execute_tool(tool, expression),
            "Calculation Tool Result: The result of 5 * 12 is 60.",
            "the calculator evaluates the extracted expression")

    tool, city = listing.route_query(QUERIES[1])
    h.equal((tool, city), ("weather", "London"), "the city after 'in' is extracted")
    h.contains(listing.execute_tool(tool, city), "15°C and cloudy",
               "the weather tool answers for London")

    tool, city = listing.route_query(QUERIES[2])
    h.equal((tool, city), ("weather", "Berlin"),
            "a city name containing 'in' is not split by the preposition")

    tool, args = listing.route_query(QUERIES[3])
    h.equal(tool, "database", "the word retrieve routes to the database tool")
    h.contains(listing.execute_tool(tool, args), "1,500 records",
               "the database tool returns the mock rows")

    tool, args = listing.route_query(QUERIES[4])
    h.equal((tool, args), (None, None), "an unrouteable query returns no tool")
    h.equal(listing.execute_tool(tool, args),
            "Agent Decision: No appropriate tool found for this query.",
            "the Act phase reports the missing tool instead of crashing")

    h.equal(listing.financial_calculator(INJECTION),
            "Calculation Tool Error: Invalid expression.",
            "the calculator refuses anything that is not arithmetic")
    h.equal(listing.financial_calculator("2 + 2"), 
            "Calculation Tool Result: The result of 2 + 2 is 4.",
            "the calculator still evaluates real arithmetic")

    responses = {query: listing.run_tool_router_agent(query) for query in QUERIES}
    h.write_json("responses.json", responses)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (tool router)", FILES).crash())
