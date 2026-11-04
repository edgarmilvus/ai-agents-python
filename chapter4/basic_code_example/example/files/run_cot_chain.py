"""Harness for the CoT chain: prompt, model and parser in one pipe.

The model is scripted, but the template and the LCEL sequence are the listing's
own: the harness checks that the prompt asks for a REASONING section and that the
chain returns what the model produced, unchanged.
"""
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import langchain_openai  # noqa: E402
import langchain_classic.memory  # noqa: E402,F401
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

warnings.simplefilter("ignore")

ANSWER = (
    "REASONING:\n"
    "The meeting is fixed at 10:00-11:00 and lunch at 12:00-13:00. The report needs "
    "three hours before 15:00, so it can start at 11:00 and end at 14:00. The code "
    "review fits in the remaining hour after 14:00.\n\n"
    "SCHEDULE:\n09:00-10:00 Preparation\n10:00-11:00 Team meeting\n"
    "11:00-14:00 Q3 report\n14:00-15:00 Code review\n12:00-13:00 Lunch"
)

CLIENT_KWARGS = []


def scripted_client(**kwargs):
    CLIENT_KWARGS.append(kwargs)
    return FakeListChatModel(responses=[ANSWER])


def main():
    h = Harness("example 1 (CoT chain)", FILES)
    langchain_openai.ChatOpenAI = scripted_client
    module = load_listing(FILES / "01_cot_chain.py", "cot_chain")

    h.contains(module.COT_TEMPLATE, "REASONING:", "the template demands a reasoning section")
    h.contains(module.COT_TEMPLATE, "{tasks}", "the template has a slot for the tasks")
    h.equal(module.prompt.input_variables, ["tasks"], "the prompt declares one input variable")

    response = module.cot_chain.invoke({"tasks": module.complex_tasks})
    h.equal(response, ANSWER, "the chain returns the model's text unchanged")
    h.contains(response, "REASONING:", "the answer carries the reasoning section")
    h.contains(module.complex_tasks, "10:00 AM", "the input carries the fixed meeting")

    kwargs = CLIENT_KWARGS[0]
    h.equal(kwargs.get("model"), module.MODEL, "the model comes from the environment")
    h.equal(kwargs.get("base_url"), module.BASE_URL, "the base URL comes from the environment")
    h.equal(kwargs.get("temperature"), 0.1, "a low temperature is configured")

    h.write_json("chain.json", {
        "template_asks_for_reasoning": "REASONING:" in module.COT_TEMPLATE,
        "answer": response,
        "model": module.MODEL,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (CoT chain)", FILES).crash())
