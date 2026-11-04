import logging
from typing import Dict, Any, List
from collections import deque

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- MOCK ENVIRONMENT & BROWSER TOOL (DRY Abstraction) ---
# Reusing the structure from Exercise 4 for the BrowserTool

class NoSuchElementException(Exception): pass
class MockDriver:
    # Simulates page state and transitions
    def __init__(self):
        self.page_number = 1
        self.elements = {
            1: {"url": "/login", "title": "Login Page", "inputs": {"email_field": "ID", "password_field": "ID"}, "button": "LoginBtn"},
            2: {"url": "/config", "title": "Configuration Wizard", "inputs": {"tier_select": "NAME"}, "button": "NextBtn"},
            3: {"url": "/review", "title": "Review Order", "inputs": {}, "button": "ConfirmBtn"},
            4: {"url": "/success", "title": "Success!", "inputs": {}, "button": None}
        }
        self.current_page_data = self.elements[1]

    def get(self, url):
        logging.debug(f"Mock Driver navigated to {url}")

    @property
    def current_url(self): return f"https://mocksite.com{self.current_page_data['url']}"
    @property
    def title(self): return self.current_page_data['title']

    def find_element(self, strategy, value):
        if value in self.current_page_data['inputs'] or value == self.current_page_data['button']:
            return MockElement(value)
        raise NoSuchElementException(f"Mock element not found: {value}")

class MockElement:
    def __init__(self, name): self.name = name
    def send_keys(self, text): logging.info(f"Mock: Text '{text}' sent to element '{self.name}'.")
    def click(self):
        global mock_driver_instance
        logging.info(f"Mock: Element '{self.name}' clicked.")
        # Simulate page transition after successful interaction
        if mock_driver_instance.page_number < 4:
            mock_driver_instance.page_number += 1
            mock_driver_instance.current_page_data = mock_driver_instance.elements[mock_driver_instance.page_number]
            logging.info(f"Mock: Page transition to {mock_driver_instance.current_page_data['url']}")
    def clear(self): pass

class BrowserTool:
    """DRY wrapper for Selenium interactions."""
    def __init__(self, driver: MockDriver):
        self.driver = driver

    def navigate_to(self, url: str) -> bool:
        self.driver.get(url)
        return True

    def click_element(self, strategy: str, value: str) -> bool:
        try:
            element = self.driver.find_element(strategy, value)
            element.click()
            return True
        except NoSuchElementException as e:
            logging.error(f"Click failed: Locator {strategy}='{value}' not found.")
            # In a real system, this would raise an exception for the agent to catch
            return False 

    def type_text(self, strategy: str, value: str, text: str) -> bool:
        try:
            element = self.driver.find_element(strategy, value)
            element.send_keys(text)
            return True
        except NoSuchElementException as e:
            logging.error(f"Type failed: Locator {strategy}='{value}' not found.")
            return False

    def get_page_state(self) -> str:
        """Returns a summarized state for the LLM Planner."""
        inputs = list(self.driver.current_page_data['inputs'].keys())
        button = self.driver.current_page_data['button']
        state = (
            f"URL: {self.driver.current_url}\n"
            f"Title: {self.driver.title}\n"
            f"Visible Elements: Input fields: {inputs}. Main Button: {button}"
        )
        return state

# Initialize the mock driver and tool
mock_driver_instance = MockDriver()
browser_tool = BrowserTool(mock_driver_instance)

# --- State Management via Memory ---
class LLMMemory:
    """Stores persistent state and interaction history."""
    def __init__(self, initial_goal: str):
        self.goal = initial_goal
        self.history = deque(maxlen=10)
        self.state = {"username": None, "tier": None, "current_page": "start"}
        self.history.append(f"Initial Goal: {initial_goal}")

    def add_interaction(self, role: str, content: str):
        self.history.append(f"[{role}]: {content}")

    def get_full_context(self) -> str:
        context = (
            f"Overall Goal: {self.goal}\n"
            f"Current Internal State: {self.state}\n"
            f"Recent History:\n" + "\n".join(self.history)
        )
        return context

# --- LLM Planner Integration (Mock) ---
def llm_planner(memory: LLMMemory, page_state: str) -> str:
    """Simulates the LLM Planner generating the next high-level action."""
    
    full_context = memory.get_full_context()
    current_page = mock_driver_instance.page_number
    
    # The LLM reasons based on memory and current page state
    if current_page == 1: # Login Page
        if memory.state['username'] is None:
            return "browser_tool.type_text('ID', 'email_field', 'user@agent.com')"
        elif 'user@agent.com' in memory.state['username']:
            return "browser_tool.click_element('ID', 'LoginBtn')"
            
    elif current_page == 2: # Configuration Page
        if memory.state['tier'] is None:
            # Goal requires 'Pro' tier
            return "browser_tool.type_text('NAME', 'tier_select', 'Pro')"
        else:
            return "browser_tool.click_element('ID', 'NextBtn')"
            
    elif current_page == 3: # Review Page
        return "browser_tool.click_element('ID', 'ConfirmBtn')"
        
    elif current_page == 4: # Success Page
        return "Task Complete"
        
    # If the page is unexpected or action failed previously, navigate back to start
    return "browser_tool.navigate_to('https://mocksite.com/login')"

def update_memory_after_action(memory: LLMMemory, action: str):
    """Updates internal state based on successful action execution."""
    if "type_text" in action:
        if 'email_field' in action:
            memory.state['username'] = 'user@agent.com'
            memory.add_interaction("Agent", "Entered credentials.")
        elif 'Pro' in action:
            memory.state['tier'] = 'Pro'
            memory.add_interaction("Agent", "Selected Pro tier based on goal.")
    
    memory.state['current_page'] = mock_driver_instance.current_page_data['url']
    memory.add_interaction("System", f"Page updated to {memory.state['current_page']}")

# --- Main Autonomous Agent Loop ---
def execute_command(command: str) -> bool:
    """Safely executes the high-level command string."""
    try:
        if command.startswith("browser_tool.type_text"):
            # Simplified parsing: assumes fixed format 'strategy', 'value', 'text'
            parts = command.split("(", 1)[1].rsplit(")", 1)[0].replace("'", "").split(",", 2)
            return browser_tool.type_text(parts[0].strip(), parts[1].strip(), parts[2].strip())
        
        elif command.startswith("browser_tool.click_element"):
            parts = command.split("(", 1)[1].rsplit(")", 1)[0].replace("'", "").split(",", 1)
            return browser_tool.click_element(parts[0].strip(), parts[1].strip())
        
        elif command.startswith("browser_tool.navigate_to"):
            url = command.split("(", 1)[1].rsplit(")", 1)[0].replace("'", "")
            return browser_tool.navigate_to(url.strip())
        
        return True
    except Exception as e:
        logging.error(f"Error executing command '{command}': {e}")
        return False

def autonomous_task_agent(initial_goal: str, max_steps: int = 10):
    """Executes the multi-page task using LLM planning and memory."""
    
    global mock_driver_instance, browser_tool
    # The tool holds a reference to its driver. Resetting only one of the two leaves
    # the agent reading the old page for the rest of the run.
    mock_driver_instance = MockDriver() # Reset state
    browser_tool = BrowserTool(mock_driver_instance)
    memory = LLMMemory(initial_goal)
    
    # Start navigation
    browser_tool.navigate_to('https://mocksite.com/login')
    
    for step in range(1, max_steps + 1):
        logging.info(f"\n--- Step {step}: {browser_tool.driver.title} ---")
        
        # 1. Capture Current State
        page_state = browser_tool.get_page_state()
        memory.add_interaction("Browser", f"Current state captured: {browser_tool.driver.current_url}")
        
        # 2. LLM Planner Determines Next Action
        action_command = llm_planner(memory, page_state)
        
        if action_command == "Task Complete":
            logging.critical("Goal achieved. Task flow successfully completed.")
            break
        
        # 3. Execute Action
        success = execute_command(action_command)
        
        if success:
            update_memory_after_action(memory, action_command)
        else:
            # 4. Error Handling and Re-planning
            error_context = f"Action '{action_command}' failed. Element not found or interaction failed. Re-planning triggered."
            memory.add_interaction("Error", error_context)
            logging.error(error_context)
            # The loop continues; the LLM Planner receives the failure context in memory
            
    if step == max_steps:
        logging.warning("Agent reached maximum steps without completing the task.")

# Example Execution
autonomous_task_agent("Log in as user X and upgrade the account to the Pro tier.")
