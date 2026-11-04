"""Harness for the starter tools the exercises begin from.

The block defines the seven tools and nothing else, so the harness composes it
with the mock services and calls each tool the way an agent would.
"""
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
SETUP = (CHAPTER / "necessary_setup_code_block/example/files" / "01_mock_services.py")


def compose(solution: pathlib.Path):
    source = SETUP.read_text() + "\n\n" + solution.read_text()
    namespace = {"__name__": "__main__"}
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), namespace)
    return namespace, log.getvalue()


def main():
    h = Harness("example 3 (exercise tools)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        ns, _ = compose(FILES / "01_exercise_tools.py")
        config_path = str(output / "config.json")
        (output / "config.json").write_text(json.dumps({"agent_name": "ToolMaster"}))

        h.contains(ns["read_json_config"](config_path), "ToolMaster",
                   "the config reader returns the file's content")
        ns["update_json_config"](config_path, "max_retries", 9)
        h.equal(json.loads(ns["read_json_config"](config_path))["max_retries"], 9,
                "the updater writes the new value back")
        h.equal(ns["update_json_config"](config_path, "extra", {"a": 1}),
                ns["update_json_config"](config_path, "extra", {"a": 1}),
                "updating the same key twice is stable")

        digest = ns["calculate_hash"]("test_data", "sha256")
        h.check(len(digest) == 64 or "sha256" in digest,
                "the hash tool accepts a supported algorithm")
        rejected = ns["calculate_hash"]("test_data", "sha1")
        h.contains(rejected, "sha1", "an unsupported algorithm is named back")
        too_big = ns["calculate_hash"]("x" * 2000, "sha256")
        h.contains(too_big, "1024", "the size guard reports the limit")

        h.contains(ns["get_stock_price"]("GOOGL"), "155.20", "the stock tool quotes GOOGL")
        h.contains(ns["check_live_service_status"]("auth_service"), "OK",
                   "the status tool reports auth_service")
        inventory = ns["query_inventory"](category="Peripherals")
        h.equal(len(json.loads(inventory)), 2, "the inventory query filters by category")
        log_report = ns["analyze_deployment_log"](ns["LOG_FILE_PATH"])
        h.contains(log_report, "2", "the log tool counts the two errors")

        h.write_json("starter.json", {
            "hash": digest,
            "inventory_peripherals": len(json.loads(inventory)),
            "log_report": log_report,
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise tools)", FILES).crash())
