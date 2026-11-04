"""Harness for the mock services the exercises run against.

The block is a library: the harness seeds the in-memory database, calls the mock
API and checks the files the exercises read and write.
"""
import json
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 2 (mock services)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        module = load_listing(FILES / "01_mock_services.py", "mock_services")

        # The block seeds the database when it is imported, so the harness only
        # reads it: seeding twice trips the unique constraint on the item name.
        session = module.Session()
        items = session.query(module.InventoryItem).all()
        h.equal(len(items), 5, "the seed inserts the five sample products")
        h.check(all(item.category for item in items), "every seeded item has a category")
        session.close()

        found = module.MockFinancialAPI.fetch_stock_price("msft")
        h.equal(found["status"], "success", "a known ticker is found, case-insensitively")
        h.equal(found["data"]["price"], 420.00, "the MSFT price is the mocked one")

        missing = module.MockFinancialAPI.fetch_stock_price("NOPE")
        h.equal(missing["status"], "error", "an unknown ticker returns an error status")

        h.equal(module.MockFinancialAPI.get_service_status("log_aggregator"), "DEGRADED",
                "the service map reports a degraded service")
        h.equal(module.MockFinancialAPI.get_service_status("nothing"), "UNKNOWN",
                "an unknown service is reported as unknown")

        config = json.loads(pathlib.Path(module.CONFIG_FILE_PATH).read_text())
        h.equal(config["agent_name"], "ToolMaster", "the config file is seeded")
        log_text = pathlib.Path(module.LOG_FILE_PATH).read_text()
        h.equal(log_text.count("ERROR:"), 2, "the deployment log carries two errors")

        h.write_json("mock_services.json", {
            "inventory_items": len(items),
            "tickers": sorted(module.MockFinancialAPI.STOCK_DATA),
            "services": module.MockFinancialAPI.SERVICE_HEALTH,
            "files": [module.CONFIG_FILE_PATH, module.LOG_FILE_PATH],
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (mock services)", FILES).crash())
