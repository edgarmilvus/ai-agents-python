"""Harness for the contextual calculator: ReAct, memory and one tool.

The listing builds a real ChatOpenAI client, so the harness swaps the class for a
scripted chat model before importing it. The loop, the prompt, the memory and the
tool are the listing's own; only the model's answers are fixed.
"""
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

# The listings use the deprecated-in-name classic APIs on purpose; the
# warning would otherwise put a site-packages path in the harness log.

import langchain_openai  # noqa: E402
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

# Import this before installing the filter: langchain resets the warning
# filters when it first loads, and the log would otherwise carry a
# site-packages path with the username in it.
import langchain_classic.memory  # noqa: E402,F401

warnings.simplefilter("ignore")

RESPONSES = [
    "Final Answer: Noted that 12 is one of your favorite numbers.",
    "Thought: I should use the tool.\nAction: calculate_square\nAction Input: 7",
    "Thought: I now know the final answer\nFinal Answer: The square of 7 is 49.",
    "Thought: The remembered number is 12.\nAction: calculate_square\nAction Input: 12",
    "Thought: I now know the final answer\nFinal Answer: The square of 12 is 144.",
]

CLIENT_KWARGS = []


def scripted_client(**kwargs):
    CLIENT_KWARGS.append(kwargs)
    return FakeListChatModel(responses=RESPONSES)


def main():
    h = Harness("example 1 (contextual calculator)", FILES)
    langchain_openai.ChatOpenAI = scripted_client
    module = load_listing(FILES / "01_contextual_calculator.py", "contextual_calculator")

    h.equal(module.response_a["output"], "Noted that 12 is one of your favorite numbers.",
            "the first turn answers without a tool")
    h.equal(module.response_b["output"], "The square of 7 is 49.", "the tool computed 7 squared")
    h.equal(module.response_c["output"], "The square of 12 is 144.",
            "the third turn recalls 12 from memory and squares it")
    h.equal(module.calculate_square.run("9"), 81,
            "the tool converts the string Action Input before multiplying")

    history = module.memory.load_memory_variables({})["chat_history"]
    h.contains(history, "Remember 12", "memory keeps the first user turn")
    h.contains(history, "144", "memory keeps the last agent turn")

    h.check(bool(CLIENT_KWARGS), "the listing built a client through the swapped class")
    kwargs = CLIENT_KWARGS[0]
    h.equal(kwargs.get("model"), module.MODEL, "the client uses the model from the environment")
    h.equal(kwargs.get("base_url"), module.BASE_URL, "the client uses the configured base URL")
    h.equal(kwargs.get("temperature"), 0, "the planner runs at temperature 0")
    h.check(kwargs.get("api_key") is None or isinstance(kwargs.get("api_key"), str),
            "the key is read from the environment, not hard-coded")

    h.write_json("trace.json", {
        "turns": [
            {"input": module.prompt_a, "output": module.response_a["output"]},
            {"input": module.prompt_b, "output": module.response_b["output"]},
            {"input": module.prompt_c, "output": module.response_c["output"]},
        ],
        "model": module.MODEL,
        "memory": history,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (contextual calculator)", FILES).crash())
