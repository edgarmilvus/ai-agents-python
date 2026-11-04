"""Harness for exercise 3: ORM inventory filtering over the seeded database."""
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
    h = Harness("exercise 3 (ORM inventory)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        ns = compose(FILES / "01_orm_inventory_agent.py")
        query = ns["query_inventory"]

        everything = json.loads(query())
        h.equal(len(everything), 5, "an unfiltered query returns the five products")

        electronics = json.loads(query(category="Electronics"))
        h.equal(len(electronics), 2, "the category filter returns two products")
        h.check(all(item["category"] == "Electronics" for item in electronics),
                "every returned row matches the category")

        expensive = json.loads(query(min_price=1000.0))
        h.equal([item["name"] for item in expensive], ["Laptop Pro X"],
                "the price filter keeps only the laptop")

        scarce = json.loads(query(max_quantity=10))
        h.equal(len(scarce), 1, "the quantity filter keeps the one product under ten units")
        h.check(scarce[0]["quantity"] <= 10, "the surviving row is inside the limit")

        none = query(category="Furniture")
        h.contains(none, "No inventory items", "an empty result is reported as such")

        h.check(list(everything[0]) == ["id", "name", "category", "price", "quantity"],
                "rows are serialised with their columns")

        h.write_json("result.json", {
            "all": len(everything),
            "electronics": [item["name"] for item in electronics],
            "expensive": [item["name"] for item in expensive],
            "scarce": [item["name"] for item in scarce],
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (ORM inventory)", FILES).crash())
