"""A stub of the Selenium surface the chapter's listings touch.

The chapter automates a real browser. The suite must not: there is no Chrome in the
container and no network in CI. This module installs the same module tree into
`sys.modules` — `selenium.webdriver`, `By`, `Keys`, `WebDriverWait`, the expected
conditions, the exceptions, `webdriver_manager` — so every import in the listings
resolves, and a scripted driver records what the agent asked the page to do.

A harness installs it, hands over a `ScriptedDriver` with its pages, then loads the
listing. Nothing here waits, screenshots a browser or downloads a binary.
"""
import pathlib
import sys
import types

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000a49444154789c6360000002000154a24f5f0000000049454e44ae426082"
)

DRIVER = None


class WebDriverException(Exception):
    pass


class NoSuchElementException(WebDriverException):
    pass


class StaleElementReferenceException(WebDriverException):
    pass


class ElementClickInterceptedException(WebDriverException):
    pass


class TimeoutException(WebDriverException):
    pass


class By:
    ID = "id"
    NAME = "name"
    XPATH = "xpath"
    CSS_SELECTOR = "css selector"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"


class Keys:
    ENTER = "\ue007"
    RETURN = "\ue006"
    TAB = "\ue004"
    SHIFT = "\ue008"
    ESCAPE = "\ue00c"


class Element:
    """One node of a scripted page, with the handful of methods listings call."""

    def __init__(self, text="", locator=None, children=None, tag="div",
                 attributes=None, on_enter=None):
        self.text = text
        self.locator = locator
        self.children = list(children or [])
        self.tag = tag
        self.attributes = dict(attributes or {})
        self.on_enter = on_enter
        self.typed = []
        self.clicks = 0
        self.cleared = 0

    def matches(self, by, value):
        if by == By.TAG_NAME:
            return self.tag == value
        return self.locator == (by, value)

    def find_element(self, by, value):
        for child in self.children:
            if child.matches(by, value):
                return child
        raise NoSuchElementException(f"no element {by}={value!r}")

    def find_elements(self, by, value):
        return [child for child in self.children if child.matches(by, value)]

    def send_keys(self, *values):
        text = "".join(str(value) for value in values if value != Keys.ENTER)
        if text:
            self.typed.append(text)
        if Keys.ENTER in values and self.on_enter is not None:
            self.on_enter(self)

    def clear(self):
        self.cleared += 1
        self.typed.clear()

    def click(self):
        self.clicks += 1

    def get_attribute(self, name):
        return self.attributes.get(name)

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def screenshot(self, path):
        pathlib.Path(path).write_bytes(PNG_1X1)


class Page:
    """A URL the scripted driver can navigate to."""

    def __init__(self, title="", url=None, elements=None, body_text="", html=""):
        self.title = title
        self.url = url
        self.elements = list(elements or [])
        self.body_text = body_text
        self.html = html

    def find(self, by, value):
        for element in self.elements:
            if element.matches(by, value):
                return element
        raise NoSuchElementException(f"no element {by}={value!r} on {self.url}")

    def find_all(self, by, value):
        return [element for element in self.elements if element.matches(by, value)]


class ScriptedDriver:
    """Stands in for `webdriver.Chrome`: same calls, no browser."""

    def __init__(self, pages=None):
        self.pages = dict(pages or {})
        self.visited = []
        self.current = None
        self.title = ""
        self.current_url = "about:blank"
        self.quit_called = False

    def get(self, url):
        page = self.pages.get(url)
        if page is None:
            raise WebDriverException(f"no page scripted for {url!r}")
        self.visited.append(url)
        self.current = page
        self.title = page.title
        self.current_url = page.url or url

    def find_element(self, by, value):
        return self.current.find(by, value)

    def find_elements(self, by, value):
        return self.current.find_all(by, value)

    def execute_script(self, script, *args):
        return None

    def save_screenshot(self, path):
        pathlib.Path(path).write_bytes(PNG_1X1)

    @property
    def page_source(self):
        return self.current.html if self.current else ""

    def quit(self):
        self.quit_called = True

    def close(self):
        self.quit_called = True


class ChromeOptions:
    def __init__(self):
        self.arguments = []
        self.experimental_options = {}

    def add_argument(self, argument):
        self.arguments.append(argument)

    def add_experimental_option(self, name, value):
        self.experimental_options[name] = value


class Service:
    def __init__(self, path=None):
        self.path = path


class ChromeDriverManager:
    def install(self):
        return "/nonexistent/chromedriver"


class FirefoxDriverManager:
    def install(self):
        return "/nonexistent/geckodriver"


class WebDriverWait:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout

    def until(self, condition):
        result = condition(self.driver) if callable(condition) else condition
        if result in (False, None):
            raise TimeoutException("condition not met")
        return result

    def until_not(self, condition):
        return True


class _ExpectedConditions:
    """The conditions the listings use, evaluated against the scripted page."""

    @staticmethod
    def presence_of_element_located(locator):
        def check(driver):
            # A real wait polls and, when nothing matches, raises TimeoutException
            # rather than letting NoSuchElementException escape.
            try:
                return driver.find_element(*locator)
            except NoSuchElementException:
                raise TimeoutException(f"not present: {locator}")
        return check

    @staticmethod
    def visibility_of_element_located(locator):
        def check(driver):
            try:
                return driver.find_element(*locator)
            except NoSuchElementException:
                raise TimeoutException(f"not visible: {locator}")
        return check

    @staticmethod
    def presence_of_all_elements_located(locator):
        def check(driver):
            found = driver.find_elements(*locator)
            if not found:
                raise TimeoutException(f"nothing matched {locator}")
            return found
        return check

    @staticmethod
    def element_to_be_clickable(target):
        def check(driver):
            if isinstance(target, Element):
                return target
            return driver.find_element(*target)
        return check

    @staticmethod
    def text_to_be_present_in_element(locator, text):
        def check(driver):
            element = driver.find_element(*locator)
            return text in element.text
        return check

    @staticmethod
    def invisibility_of_element_located(locator):
        def check(driver):
            return True
        return check


def _module(name, **attributes):
    module = types.ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def set_driver(driver):
    """The driver `webdriver.Chrome(...)` will return."""
    global DRIVER
    DRIVER = driver
    return driver


def _chrome(*args, **kwargs):
    if DRIVER is None:
        raise WebDriverException("no scripted driver installed")
    return DRIVER


def install():
    """Create the `selenium` and `webdriver_manager` module trees."""
    exceptions = _module(
        "selenium.common.exceptions",
        WebDriverException=WebDriverException,
        NoSuchElementException=NoSuchElementException,
        StaleElementReferenceException=StaleElementReferenceException,
        ElementClickInterceptedException=ElementClickInterceptedException,
        TimeoutException=TimeoutException,
    )
    common = _module("selenium.common", exceptions=exceptions)

    by = _module("selenium.webdriver.common.by", By=By)
    keys = _module("selenium.webdriver.common.keys", Keys=Keys)
    webdriver_common = _module("selenium.webdriver.common", by=by, keys=keys)

    service = _module("selenium.webdriver.chrome.service", Service=Service)
    options = _module("selenium.webdriver.chrome.options", Options=ChromeOptions)
    chrome = _module("selenium.webdriver.chrome", service=service, options=options)
    chrome.service = service
    chrome.options = options

    conditions = _module("selenium.webdriver.support.expected_conditions",
                         **{name: getattr(_ExpectedConditions, name)
                            for name in dir(_ExpectedConditions) if not name.startswith("_")})
    ui = _module("selenium.webdriver.support.ui", WebDriverWait=WebDriverWait)
    support = _module("selenium.webdriver.support", ui=ui,
                      expected_conditions=conditions)

    webdriver = _module(
        "selenium.webdriver",
        Chrome=_chrome,
        Firefox=_chrome,
        ChromeOptions=ChromeOptions,
        By=By,
        Keys=Keys,
        common=webdriver_common,
        chrome=chrome,
        support=support,
        Service=Service,
        WebDriverWait=WebDriverWait,
    )

    selenium = _module("selenium", webdriver=webdriver, common=common)

    manager = _module("webdriver_manager.chrome", ChromeDriverManager=ChromeDriverManager)
    firefox_manager = _module("webdriver_manager.firefox",
                              GeckoDriverManager=FirefoxDriverManager)
    _module("webdriver_manager", chrome=manager, firefox=firefox_manager)

    return selenium, webdriver
