"""Harness for the exercise boilerplate.

It is a library, not a demo: the points worth asserting are that the mocks behave
as the four exercises assume — the plan branch answers, the store retrieves, the
cart keeps state and the step counter counts.
"""
import json
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

PLAN_LINES = "\n".join(f"{number}. step {number}" for number in range(1, 5))


def main():
    h = Harness("example 3 (exercise boilerplate)", FILES)
    module = load_listing(FILES / "01_boilerplate_code_for_exercises.py", "boilerplate")

    llm = module.MockLLM({"hello": "world"})
    h.equal(llm.invoke("Say hello to the room"), "world",
            "a scripted substring wins over the default answer")
    h.equal(llm("again hello"), "world", "call() and invoke() share one path")

    plan = json.loads(module.MockLLM().invoke(
        "Please decompose the following high-level goal: analyse TSLA"
    ))
    h.equal(len(plan["plan"]), 3, "the default branch returns the three-step plan")
    h.equal(plan["plan"][1]["tool"], "CalculateMovingAverage",
            "the plan names the tool each step needs")

    store = module.MockVectorStore()
    h.equal(len(store.similarity_search("project risk")), 2, "a risk query retrieves two practices")
    h.equal(len(store.similarity_search("lunch plans")), 1, "an unrelated query falls back")

    reflector = module.ProjectRiskReflector(vector_store=store)
    reflection = reflector.run("we have a risk of slipping")
    h.contains(reflection, "Retrieved Best Practices:", "the reflector labels its output")
    h.contains(reflection, "change requests", "the reflector returns retrieved documents")

    prices = module.StockPriceLookup().run(ticker="TSLA", period="1y")
    h.equal(json.loads(prices)["data_points"], 250, "the price tool answers for TSLA")
    average = module.CalculateMovingAverage().run(price_data_json=prices, window=50)
    h.contains(average, "50-day moving average", "the average tool consumes the price JSON")

    cart = module.ShoppingCartTool()
    h.contains(cart.view_cart(), "empty", "a new cart is empty")
    h.contains(cart.run("add_item", item_name="Apple", quantity=2), "Added 2 x Apple",
            "run() dispatches add_item")
    h.equal(len(cart.items), 1, "the item is stored on the tool instance")
    h.contains(cart.run("view_cart"), "2 x Apple", "run() dispatches view_cart")
    h.contains(cart.run("checkout"), "Cart cleared", "run() dispatches checkout")
    h.equal(cart.items, [], "checkout resets the state")
    try:
        cart.run("explode")
        h.check(False, "an unknown action must raise")
    except ValueError:
        h.check(True, "an unknown action raises instead of failing silently")

    counter = module.PlanStepCounter()
    h.equal(counter.run(PLAN_LINES), 4, "the counter counts numbered steps")
    h.equal(counter.run(
        "Research three different investment strategies and compare them"), 6,
        "the deliberately complex plan trips the constraint")

    h.write_json("boilerplate.json", {
        "classes": ["MockLLM", "MockVectorStore", "ProjectRiskReflector", "BaseTool",
                    "StockPriceLookup", "CalculateMovingAverage", "ShoppingCartTool",
                    "PlanStepCounter"],
        "plan_steps": len(plan["plan"]),
        "counter_on_four_steps": 4,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise boilerplate)", FILES).crash())
