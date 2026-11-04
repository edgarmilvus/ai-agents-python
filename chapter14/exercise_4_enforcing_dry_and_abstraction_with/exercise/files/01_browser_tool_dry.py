import logging
from typing import Dict, Any

# --- MOCKING SELENIUM COMPONENTS ---
# We use mock classes to define the interface without requiring actual Selenium setup
class MockWebDriver:
    def get(self, url): pass
    def find_element(self, by, value): 
        if value == "fail_id":
            raise NoSuchElementException(f"Mock failure finding {value}")
        return MockElement(value)
    @property
    def title(self): return "Mock Page Title"
    @property
    def current_url(self): return "https://mock.com/current"
    def find_elements(self, by, value): return [MockElement("header1")]
    def __init__(self): logging.debug("Mock WebDriver initialized.")

class MockElement:
    def __init__(self, value): self.value = value
    def click(self): logging.info(f"Mock Click: {self.value}")
    def send_keys(self, text): logging.info(f"Mock Send Keys: {self.value} received '{text}'")
    def clear(self): pass
    @property
    def text(self): return "This is the main body content of the page."

# Mock Selenium Exceptions and Waits
class NoSuchElementException(Exception): pass
class TimeoutException(Exception): pass
class WebDriverException(Exception): pass

class MockWait:
    def __init__(self, driver, timeout): pass
    def until(self, condition):
        if condition[1] == "fail_id":
            raise TimeoutException("Mock timeout")
        return MockElement(condition[1])

class EC:
    @staticmethod
    def visibility_of_element_located(locator): return locator
    @staticmethod
    def element_to_be_clickable(element): return element

class By:
    ID = "id"
    NAME = "name"
    XPATH = "xpath"
    CSS_SELECTOR = "css_selector"
    LINK_TEXT = "link_text"

# Configure logging for the tool
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BrowserTool:
    """
    A robust wrapper around the Selenium WebDriver, enforcing DRY principles
    and centralizing error handling for autonomous agent interactions.
    """
    
    # Internal mapping for Selenium By strategies
    LOCATOR_MAPPING = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "CSS_SELECTOR": By.CSS_SELECTOR,
        "LINK_TEXT": By.LINK_TEXT,
    }

    def __init__(self, driver: MockWebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = MockWait(self.driver, timeout) # Uses MockWait for simulation
        self.timeout = timeout
        logging.info("BrowserTool initialized successfully.")

    def _get_by_strategy(self, strategy: str):
        """Maps string strategy to Selenium By object."""
        strategy = strategy.upper()
        if strategy not in self.LOCATOR_MAPPING:
            raise ValueError(f"Invalid locator strategy: {strategy}. Must be one of {list(self.LOCATOR_MAPPING.keys())}")
        return self.LOCATOR_MAPPING[strategy]

    def _find_element_robust(self, strategy: str, value: str):
        """Waits for element visibility and returns the element."""
        by = self._get_by_strategy(strategy)
        try:
            # Simulate explicit wait conditions
            element = self.wait.until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Timeout: Element not visible using {strategy}='{value}' within {self.timeout}s.")
            # Re-raise as NoSuchElementException for consistent agent handling
            raise NoSuchElementException(f"Element not found after wait: {value}") 
        except NoSuchElementException:
            logging.error(f"No Such Element: Could not find element using {strategy}='{value}'.")
            raise
        except WebDriverException as e:
            logging.error(f"WebDriver Error finding element {strategy}='{value}': {e}")
            raise

    def navigate_to(self, url: str) -> bool:
        """Navigates the browser to the specified URL."""
        try:
            self.driver.get(url)
            logging.info(f"Navigated to: {url}")
            return True
        except WebDriverException as e:
            logging.error(f"Navigation failed for {url}: {e}")
            return False

    def click_element(self, strategy: str, value: str) -> bool:
        """Locates and clicks an element, ensuring it is clickable."""
        try:
            element = self._find_element_robust(strategy, value)
            # Simulate clickability check
            EC.element_to_be_clickable(element)
            element.click()
            return True
        except Exception as e:
            logging.error(f"Click failed for {strategy}='{value}'. Error: {e.__class__.__name__}: {e}")
            return False

    def type_text(self, strategy: str, value: str, text: str) -> bool:
        """Locates an input field, clears it, and types the text."""
        try:
            element = self._find_element_robust(strategy, value)
            element.clear()
            element.send_keys(text)
            logging.info(f"Typed text into input {strategy}='{value}'.")
            return True
        except Exception as e:
            logging.error(f"Typing failed for {strategy}='{value}'. Error: {e.__class__.__name__}: {e}")
            return False

    def get_page_content_summary(self) -> Dict[str, str]:
        """
        Returns a structured summary of the current page suitable for LLM consumption.
        """
        try:
            title = self.driver.title
            url = self.driver.current_url
            
            # Retrieve limited text snippet
            main_content = self.driver.find_element(By.TAG_NAME, 'body').text[:200]
            
            summary = {
                "url": url,
                "title": title,
                "main_text_snippet": main_content,
                "current_status": "Ready for action."
            }
            return summary
        except Exception as e:
            logging.warning(f"Failed to retrieve full page summary: {e}")
            return {"url": self.driver.current_url, "title": "Error retrieving title", "current_status": "Page content retrieval failed."}

# --- Demonstration of LLM Interface Simplification ---

def demonstrate_tool_use():
    """Shows how the LLM's plan is simplified by using the BrowserTool."""
    print("\n--- Exercise 4: LLM Interface Abstraction Demonstration ---")
    
    driver = MockWebDriver() 
    browser_tool = BrowserTool(driver)
    
    # 1. LLM Plan Output (High-level Command 1)
    command_1 = "browser_tool.type_text('ID', 'username_input', 'agent_user')"
    print(f"LLM Generates (High-level, DRY): {command_1}")
    
    # Execution (Internal logic handles 'ID' mapping and error checking)
    browser_tool.type_text('ID', 'username_input', 'agent_user') 

    # 2. LLM Plan Output (High-level Command 2)
    command_2 = "browser_tool.click_element('XPATH', '//button[text()=\"Submit\"]')"
    print(f"LLM Generates (High-level, DRY): {command_2}")
    
    # Execution
    browser_tool.click_element('XPATH', '//button[text()="Submit"]')
    
    # 3. Demonstration of Centralized Error Handling
    print("\nAttempting action with known failure ID...")
    failure_command = "browser_tool.click_element('ID', 'fail_id')"
    browser_tool.click_element('ID', 'fail_id')

# Example Execution
demonstrate_tool_use()
