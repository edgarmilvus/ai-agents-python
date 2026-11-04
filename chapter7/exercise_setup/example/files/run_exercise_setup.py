"""Harness for the exercise-setup snippet.

It is configuration, not a crew: the harness checks that the shared dict points at
the gateway and that no secret is hard-coded.
"""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 3 (exercise setup)", FILES)
    module = load_listing(FILES / "01_exercise_setup.py", "exercise_setup")

    config = module.llm_config
    h.check(config["model"].startswith("openai/"), "the model selects the OpenAI-compatible provider")
    h.equal(config["base_url"], module.BASE_URL, "the base URL comes from the environment")
    h.check("api_key" in config, "the key is passed through from the environment")
    h.equal(config.get("temperature"), 0.2, "the shared temperature is 0.2")
    h.equal(config["model"], f"openai/{module.MODEL}", "the model string is built from the env var")
    h.check("gpt-" not in config["model"], "no vendor model is hard-coded")

    h.write_json("result.json", {"model": config["model"], "base_url": config["base_url"]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (exercise setup)", FILES).crash())
