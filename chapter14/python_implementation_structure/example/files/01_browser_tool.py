import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

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

    def __init__(self, driver: webdriver.Chrome, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout)
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
            element = self.wait.until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Timeout: Element not visible using {strategy}='{value}' within {self.timeout}s.")
            raise
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
            self.wait.until(EC.element_to_be_clickable(element)).click()
            logging.info(f"Clicked element using {strategy}='{value}'.")
            return True
        except Exception as e:
            logging.error(f"Click failed for {strategy}='{value}'. Error: {e}")
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
            logging.error(f"Typing failed for {strategy}='{value}'. Error: {e}")
            return False

    def get_page_content_summary(self) -> dict:
        """
        Returns a structured summary of the current page suitable for LLM consumption.
        This prevents passing the full, token-heavy DOM.
        """
        try:
            title = self.driver.title
            url = self.driver.current_url
            
            # Retrieve key structural elements (e.g., headers, main forms)
            main_content = self.driver.find_element(By.TAG_NAME, 'body').text[:1000] # Limit size
            
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

# --- Demonstration of LLM Interaction Abstraction ---

def demonstrate_tool_use():
    # Setup mock driver (in a real scenario, this would be initialized)
    # driver = webdriver.Chrome() 
    # For demonstration, we simulate the interaction
    
    # Initialize the tool
    # browser_tool = BrowserTool(driver)
    
    # Scenario: The LLM decides to log in.
    
    # 1. LLM Plan Output (High-level Command 1)
    print("--- LLM Plan 1: Navigate ---")
    command_1 = "browser_tool.navigate_to('https://mock-login.com')"
    print(f"LLM Generates: {command_1}")
    # Execute command (simulated)
    # browser_tool.navigate_to('https://mock-login.com') 

    # 2. LLM Plan Output (High-level Command 2)
    print("\n--- LLM Plan 2: Enter Username ---")
    command_2 = "browser_tool.type_text('ID', 'username_input', 'agent_user')"
    print(f"LLM Generates: {command_2}")
    # Execute command (simulated)
    # browser_tool.type_text('ID', 'username_input', 'agent_user') 
    
    # 3. LLM Plan Output (High-level Command 3)
    print("\n--- LLM Plan 3: Click Submit ---")
    command_3 = "browser_tool.click_element('XPATH', '//button[text()=\"Login\"]')"
    print(f"LLM Generates: {command_3}")
    # Execute command (simulated)
    # browser_tool.click_element('XPATH', '//button[text()="Login"]')

# demonstrate_tool_use()
