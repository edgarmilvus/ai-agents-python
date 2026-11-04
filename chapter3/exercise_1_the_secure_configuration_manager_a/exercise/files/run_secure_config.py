"""Harness for exercise 1: reading and updating a JSON configuration file."""
import json
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 1 (secure config)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        module = load_listing(FILES / "01_secure_config_agent.py", "secure_config")
        path = str(output / "agent_config.json")
        if pathlib.Path(path).exists():
            pathlib.Path(path).unlink()

        h.contains(module.read_json_config(path), "not found",
                   "reading a missing file reports it instead of raising")
        h.contains(module.update_json_config(path, "agent_name", "ToolMaster"), "agent_name",
                   "the updater reports the key it wrote")
        h.equal(json.loads(module.read_json_config(path))["agent_name"], "ToolMaster",
                "the written value can be read back")
        module.update_json_config(path, "max_retries", 5)
        snapshot = json.loads(module.read_json_config(path))
        h.equal(snapshot["max_retries"], 5, "a second key is added without losing the first")
        h.equal(snapshot["agent_name"], "ToolMaster", "the first key survives the update")

        pathlib.Path(path).write_text("{not json")
        h.contains(module.read_json_config(path), "not valid JSON",
                   "a corrupt file is reported, not parsed")
        h.contains(module.update_json_config(path, "x", 1), "corrupt",
                   "updating a corrupt file refuses instead of overwriting it")

        h.write_json("result.json", {"config_after_updates": snapshot})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (secure config)", FILES).crash())
