"""Harness for the basic Selenium flow.

The listing drives a real Chrome. Here `tools/fake_selenium.py` stands in for the
driver: the page is scripted, the search box records what was typed, and pressing
ENTER navigates to a results page the same way the site would.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

import fake_selenium as fs  # noqa: E402

BASE = "https://www.wikipedia.org/"
RESULTS = "https://en.wikipedia.org/wiki/Python_Autonomous_Agents"


def main():
    h = Harness("example 1 (browser flow)", FILES)
    fs.install()

    driver = fs.set_driver(fs.ScriptedDriver())
    search_box = fs.Element(locator=(fs.By.ID, "searchInput"))
    driver.pages[BASE] = fs.Page(title="Wikipedia", url=BASE, elements=[search_box])
    driver.pages[RESULTS] = fs.Page(title="Python Autonomous Agents - Wikipedia",
                                    url=RESULTS)
    search_box.on_enter = lambda element: driver.get(RESULTS)

    module = load_listing(FILES / "01_digital_librarian.py", "digital_librarian")
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module.run_basic_automation()
    printed = log.getvalue()

    h.equal(driver.visited, [BASE, RESULTS], "the agent navigated, then the search submitted")
    h.equal(search_box.typed, ["Python Autonomous Agents"], "the query was typed into the search box")
    h.contains(printed, "[NAV] Initial Page Title: 'Wikipedia'", "the first page title was read")
    h.contains(printed, "[ACTION] Submitted search for", "the ENTER press was reported")
    h.contains(printed, "Final Page Title: Python Autonomous Agents - Wikipedia",
               "the results page was reached")
    h.check("[ERROR]" not in printed, "no step raised")
    h.check(driver.quit_called, "the browser was closed")

    h.write_json("result.json", {"visited": driver.visited, "typed": search_box.typed})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (browser flow)", FILES).crash())
