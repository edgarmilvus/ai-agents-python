"""Harness for the autonomous job filter.

Both sides of the listing are replaced, for the same reason the chapter mocks them:
there is no browser and no key here. The driver is scripted with two job cards, and
`ChatOpenAI` becomes a `FakeListChatModel` that answers with the two JSON decisions
the parser expects. The prompt, the parser and the decision logic are the listing's.
"""
import contextlib
import io
import json
import os
import pathlib
import sys
import time

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

import fake_selenium as fs  # noqa: E402
import langchain_openai  # noqa: E402
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

URL = "https://example-job-board.com/listings"

MATCH = json.dumps({
    "is_match": True,
    "reasoning": "Senior title, Python and Django, and the posting mentions global teams.",
})
NO_MATCH = json.dumps({
    "is_match": False,
    "reasoning": "The description is a Java role with no remote signal.",
})


def card(title, description):
    return fs.Element(
        locator=(fs.By.CLASS_NAME, "job-card-container"),
        children=[
            fs.Element(text=title, locator=(fs.By.CLASS_NAME, "job-title")),
            fs.Element(text=description,
                       locator=(fs.By.CLASS_NAME, "job-description-snippet")),
        ],
    )


def main():
    h = Harness("example 2 (job filter agent)", FILES)
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    fs.install()

    driver = fs.set_driver(fs.ScriptedDriver())
    driver.pages[URL] = fs.Page(
        title="Job board",
        url=URL,
        elements=[
            card("Senior Python Engineer", "Python, Django, global teams."),
            card("Java Developer", "Java and R, on site."),
        ],
    )

    model = FakeListChatModel(responses=[MATCH, NO_MATCH])
    langchain_openai.ChatOpenAI = lambda **kwargs: model

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "job_filter_agent", str(FILES / "01_job_filter_agent.py"))
    module = importlib.util.module_from_spec(spec)

    real_sleep = time.sleep
    time.sleep = lambda *_: None
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            spec.loader.exec_module(module)
            agent = module.AutonomousJobFilter(criteria=module.SEARCH_CRITERIA)
            agent.run_agent(url=URL)
            agent.close()
    finally:
        time.sleep = real_sleep
    printed = log.getvalue()

    h.contains(printed, "Found 2 potential job postings", "both cards were read from the page")
    h.contains(printed, "Title Extracted: Senior Python Engineer", "the card's title came from Selenium")
    h.contains(printed, "[LLM Decision] Match: True", "the first posting was judged a match")
    h.contains(printed, ">> MATCH FOUND", "the match was acted on")
    h.contains(printed, "[LLM Decision] Match: False", "the second posting was rejected")
    h.contains(printed, ">> NO MATCH", "the rejection was reported")
    h.check("[Warning]" not in printed and "[Error]" not in printed,
            "neither the extraction nor the parsing failed")
    h.check(driver.quit_called, "the browser was closed")
    h.check(isinstance(agent.llm, FakeListChatModel), "the chat client is the fake, not a network client")

    h.write_json("result.json", {"postings": 2, "visited": driver.visited})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (job filter agent)", FILES).crash())
