import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
# We use webdriver_manager to handle the necessary browser driver binary
from webdriver_manager.chrome import ChromeDriverManager 

# --- 1. Configuration and Setup ---

# Define the target URL for automation
TARGET_URL = "https://www.wikipedia.org/" 
SEARCH_QUERY = "Python Autonomous Agents"

def run_basic_automation():
    """
    Initializes Selenium, performs a search action, and closes the browser.
    """
    driver = None
    try:
        # 1.1 Initialize the WebDriver Service
        # ChromeDriverManager() ensures the correct version of the ChromeDriver 
        # binary is downloaded and installed automatically.
        service = ChromeService(ChromeDriverManager().install())
        
        # 1.2 Configure Chrome Options
        chrome_options = webdriver.ChromeOptions()
        # Ensure the browser runs in the background (headless) for server environments
        # Comment this out if you want to watch the browser actions live
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 1.3 Start the WebDriver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"[STATUS] WebDriver initialized successfully.")
        
        # --- 2. Navigation ---
        
        # The driver navigates to the specified URL. This command blocks until the 
        # initial page load is complete (or times out).
        driver.get(TARGET_URL)
        
        # Check the page title to confirm successful navigation
        initial_title = driver.title
        print(f"[NAV] Initial Page Title: '{initial_title}'")
        
        # --- 3. Interaction (Locating and Typing) ---
        
        # 3.1 Locate the search input field
        # We use By.ID because 'searchInput' is a unique, stable identifier on Wikipedia.
        # This is the crucial step of translating a human goal into a programmatic location.
        search_box = driver.find_element(By.ID, "searchInput")
        
        print(f"[ACTION] Found search box element.")
        
        # 3.2 Send the search query
        search_box.send_keys(SEARCH_QUERY)
        
        # 3.3 Submit the form by simulating the ENTER key press
        # Keys is an enumeration of special keyboard keys.
        search_box.send_keys(Keys.ENTER)
        
        print(f"[ACTION] Submitted search for: '{SEARCH_QUERY}'")
        
        # --- 4. Verification and Cleanup ---
        
        # Simple, non-robust wait to allow the results page to load
        time.sleep(3)
        
        # Verify the new URL and title
        final_url = driver.current_url
        final_title = driver.title
        
        print(f"[RESULT] Final URL: {final_url}")
        print(f"[RESULT] Final Page Title: {final_title}")
        
    except Exception as e:
        # Catch any errors during the process (e.g., element not found, driver failure)
        print(f"[ERROR] An error occurred during automation: {e}")
        
    finally:
        # 4.1 Ensure the browser is closed
        if driver:
            driver.quit()
            print("[STATUS] WebDriver session closed successfully.")

if __name__ == "__main__":
    run_basic_automation()
