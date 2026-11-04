import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# LangChain/AI Integration Libraries
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# --- 1. Define the Structured Output Schema (Pydantic) ---
# This ensures the LLM returns a reliable, parsable JSON structure.
class JobMatchDecision(BaseModel):
    """Schema for the LLM's decision on a job posting."""
    is_match: bool = Field(description="True if the job meets all criteria, False otherwise.")
    reasoning: str = Field(description="A concise explanation of why the job was or was not a match.")

# --- 2. Configuration and Setup ---
# The endpoint, model and key come from the environment, so the same listing runs
# against any OpenAI-compatible gateway. The default is the model this volume uses.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY")
if not OPENAI_COMPATIBLE_API_KEY:
    raise ValueError("OPENAI_COMPATIBLE_API_KEY environment variable not set.")

TARGET_URL = "https://example-job-board.com/listings" # Placeholder URL
SEARCH_CRITERIA = """
The ideal job must meet three subjective criteria:

1. The title must clearly indicate a 'Senior' or 'Lead' role.
2. The description must mention Python, Django, or Flask (but not R or Java).
3. The language must subtly suggest remote work is possible (e.g., 'global teams,' 'flexible schedule,' or 'work from anywhere'), even if not explicitly tagged 'Remote'.
"""

# --- 3. The Autonomous Agent Class ---
class AutonomousJobFilter:
    def __init__(self, criteria: str):
        self.criteria = criteria
        
        # Initialize Selenium WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 15)
        
        # Initialize LLM and Parser
        self.llm = ChatOpenAI(temperature=0.1, model=MODEL,
                             base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=JobMatchDecision)
        
        # Define the prompt template for the LLM
        self.prompt_template = PromptTemplate(
            template="""
            You are an expert job filter agent. Analyze the following job posting text
            against the provided criteria. Return your analysis in the required JSON format.
            
            CRITERIA: {criteria}
            
            POSTING TEXT:
            ---
            Title: {title}
            Description: {description}
            ---
            
            {format_instructions}
            """,
            input_variables=["criteria", "title", "description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def _analyze_posting_with_ai(self, title: str, description: str) -> JobMatchDecision:
        """Sends job text to the LLM for structured decision-making."""
        
        # 3.1. Create the final prompt
        prompt_input = self.prompt_template.format_prompt(
            criteria=self.criteria,
            title=title,
            description=description
        )
        
        # 3.2. Invoke the LLM
        output = self.llm.invoke(prompt_input)
        
        # 3.3. Parse the structured output
        try:
            decision = self.parser.parse(output.content)
            print(f"   [LLM Decision] Match: {decision.is_match}")
            return decision
        except Exception as e:
            print(f"   [Error] Failed to parse LLM output: {e}")
            # Return a default 'False' decision on parsing failure for safety
            return JobMatchDecision(is_match=False, reasoning="Parsing failed.")

    def run_agent(self, url: str):
        """Main execution loop for the browser agent."""
        print(f"Navigating to {url}...")
        self.driver.get(url)
        
        # Simulate finding all job containers (Requires site-specific selector)
        try:
            # Wait for the main list of job items to load
            job_list_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-container"))
            )
            print(f"Found {len(job_list_elements)} potential job postings.")
        except Exception:
            print("Could not find job containers. Exiting.")
            return

        processed_count = 0
        for i, element in enumerate(job_list_elements):
            processed_count += 1
            print(f"\n--- Processing Job {processed_count} ---")
            
            # 4.1. Extract raw text data using Selenium
            try:
                # Assuming the title and description are nested within the container
                title = element.find_element(By.CLASS_NAME, "job-title").text
                description = element.find_element(By.CLASS_NAME, "job-description-snippet").text
                print(f"   Title Extracted: {title[:50]}...")
            except Exception as e:
                print(f"   [Warning] Failed to extract details from element {i}: {e}. Skipping.")
                continue

            # 4.2. Delegate the decision to the AI
            decision_result = self._analyze_posting_with_ai(title, description)
            
            # 4.3. Act based on the autonomous decision
            if decision_result.is_match:
                print(f"   >> MATCH FOUND! Reason: {decision_result.reasoning}")
                # In a real application, we would now click the link, save the URL, or apply.
            else:
                print(f"   >> NO MATCH. Reason: {decision_result.reasoning}")

            # Introduce a small delay to mimic human browsing behavior and avoid rate limiting
            time.sleep(1)

    def close(self):
        """Cleanly closes the browser."""
        self.driver.quit()

# --- 5. Execution Block ---
if __name__ == "__main__":
    agent = AutonomousJobFilter(criteria=SEARCH_CRITERIA)
    try:
        agent.run_agent(url=TARGET_URL)
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
    finally:
        agent.close()
