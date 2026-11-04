"""Harness for the BrowserTool structure.

The block defines the wrapper and leaves every call commented out, so the harness is
what exercises it: navigate, type, click and summarise against a scripted driver,
then the two failure paths — an unknown strategy and a missing element.
"""
import contextlib
import io
import logging
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import fake_selenium as fs  # noqa: E402

URL = "https://mock-login.com"


def main():
    h = Harness("example 3 (BrowserTool)", FILES)
    logs = io.StringIO()
    handler = logging.StreamHandler(logs)
    logging.getLogger().addHandler(handler)
    fs.install()

    driver = fs.set_driver(fs.ScriptedDriver())
    username = fs.Element(locator=(fs.By.ID, "username_input"), tag="input")
    submit = fs.Element(locator=(fs.By.XPATH, '//button[text()="Login"]'), tag="button")
    body = fs.Element(locator=(fs.By.TAG_NAME, "body"), tag="body",
                      text="Mock login page. Sign in to continue.")
    driver.pages[URL] = fs.Page(title="Mock Login", url=URL,
                                elements=[username, submit, body])

    module = load_listing(FILES / "01_browser_tool.py", "browser_tool")
    tool = module.BrowserTool(driver, timeout=2)

    h.equal(tool.navigate_to(URL), True, "navigation succeeded")
    h.equal(tool.type_text("ID", "username_input", "agent_user"), True,
            "the username was typed")
    h.equal(username.typed, ["agent_user"], "the text reached the input element")
    h.equal(tool.click_element("XPATH", '//button[text()="Login"]'), True,
            "the submit button was clicked")
    h.equal(submit.clicks, 1, "the click reached the button")

    summary = tool.get_page_content_summary()
    h.equal(summary["url"], URL, "the summary reports the current url")
    h.equal(summary["title"], "Mock Login", "the summary reports the page title")
    h.contains(summary["main_text_snippet"], "Sign in", "the summary carries the page text")
    h.equal(summary["current_status"], "Ready for action.", "the summary states its status")

    h.equal(tool.click_element("ID", "missing_button"), False,
            "a missing element is reported, not raised")
    try:
        tool._get_by_strategy("MAGIC")
    except ValueError as exc:
        h.contains(str(exc), "Invalid locator strategy", "an unknown strategy is named")
    else:
        h.check(False, "an unknown strategy should raise ValueError")

    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        module.demonstrate_tool_use()
    logging.getLogger().removeHandler(handler)
    h.contains(printed.getvalue(), "LLM Generates:", "the demo prints its plans")
    h.contains(logs.getvalue(), "Timeout: Element not visible",
               "the failure path logs the timeout")

    h.write_json("result.json", {"summary": summary})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 3 (BrowserTool)", FILES).crash())
