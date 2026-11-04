# exercise_4_custom_tool_agent.py

import configparser
from typing import Type
from pydantic import BaseModel, Field
import os

# --- 1. Simulated Configuration File Setup ---

CONFIG_FILE_NAME = 'app_config.ini'

def setup_config_file():
    """Creates the app_config.ini file for the tool to read."""
    config_content = """
[SYSTEM]
MAX_THREADS = 8
LOG_LEVEL = INFO
TIMEOUT_SECONDS = 30

[DATABASE]
PORT = 5432
RETRIES = 5
"""
    with open(CONFIG_FILE_NAME, 'w') as f:
        f.write(config_content.strip())
    print(f"Created configuration file: {CONFIG_FILE_NAME}")

# --- 2. Custom Tool Implementation ---

# Tool Input Schema Definition
class ConfigReadInput(BaseModel):
    """Input schema for the ConfigFileReaderTool."""
    section: str = Field(description="The section header in the INI file (e.g., 'SYSTEM').")
    key: str = Field(description="The specific configuration key to retrieve (e.g., 'LOG_LEVEL').")

# Custom Tool Class
class ConfigFileReaderTool:
    """
    A specialized tool designed to read specific key-value pairs from the local 
    'app_config.ini' file. It cannot access external networks.
    """
    name = "Config_File_Reader"
    description = (
        "Use this tool ONLY when you need to retrieve a specific configuration "
        "value (key) from a named section within the internal 'app_config.ini' file. "
        "Requires 'section' and 'key' as input."
    )
    args_schema: Type[BaseModel] = ConfigReadInput

    def run(self, section: str, key: str) -> str:
        """Reads the configuration file."""
        config = configparser.ConfigParser()
        
        if not os.path.exists(CONFIG_FILE_NAME):
            return f"Error: Configuration file '{CONFIG_FILE_NAME}' not found."

        try:
            config.read(CONFIG_FILE_NAME)
        except Exception as e:
            return f"Error reading configuration file: {e}"

        section = section.upper()
        key = key.upper()

        if section not in config:
            return f"Error: Configuration section '{section}' not found."
        
        if key not in config[section]:
            return f"Error: Key '{key}' not found in section '{section}'."

        return f"Configuration Value: {section}.{key} = {config[section][key]}"

# --- 3. Agent Simulation and Reasoning ---

AGENT_ROLE = """
You are the System Configuration Analyst. Your primary function is to analyze 
internal system configurations using the provided tools and provide expert advice 
based on general security and performance best practices. You must use the 
Config_File_Reader tool to retrieve configuration values before providing advice.
"""

def run_config_analyst_agent(prompt: str, tool: ConfigFileReaderTool) -> str:
    """Simulates the agent's full thought process and tool usage."""
    
    print("--- Agent Reasoning Trace Start ---")
    print(f"Agent Role: {AGENT_ROLE.splitlines()[1].strip()}")
    print(f"Query: {prompt}")
    
    # Step 1: Reasoning (Agent decides tool use based on prompt and tool description)
    print("\n[Step 1: Agent Reasoning]")
    print("I need the current logging level. The 'Config_File_Reader' tool is specialized for reading internal keys (LOG_LEVEL) from the configuration file. I must call it with section='SYSTEM' and key='LOG_LEVEL'.")
    
    tool_section = "SYSTEM"
    tool_key = "LOG_LEVEL"
    
    print(f"Tool Call: Config_File_Reader.run(section='{tool_section}', key='{tool_key}')")
    
    # Step 2: Tool Execution
    tool_output = tool.run(section=tool_section, key=tool_key)
    print(f"\n[Step 2: Tool Output]")
    print(f"Tool Result: {tool_output}")
    
    # Extract the value
    current_level = tool_output.split('= ')[-1].strip() if 'Configuration Value' in tool_output else "UNKNOWN"
    
    # Step 3: Synthesis and Advice
    print("\n[Step 3: Synthesis and Final Report]")
    
    advice = f"""
    The current logging level, retrieved from the internal configuration file using the Config_File_Reader tool, is: **{current_level}**.

    **Analysis of Changing LOG_LEVEL to DEBUG:**

    
    1.  **Security Risk:** Moving to DEBUG in production environments significantly increases the risk of data leakage. Debug logs often contain sensitive information (API keys, PII, detailed stack traces) that should not be exposed.
    
    2.  **Performance Impact:** DEBUG logging generates voluminous data, leading to high I/O utilization and increased latency, which can severely impact application performance and rapid disk consumption.
    
    **Recommendation:**
    The system should maintain **INFO** for standard operations. DEBUG should only be used temporarily in controlled staging environments for deep troubleshooting.
    """
    
    print("--- Agent Reasoning Trace End ---")
    return advice.strip()

# --- Execution ---
if __name__ == "__main__":
    
    # Setup the required file
    setup_config_file()
    
    # Instantiate the custom tool
    config_tool = ConfigFileReaderTool()
    
    AGENT_PROMPT = "What is the current logging level in the system configuration, and what are the security implications of changing it to DEBUG?"
    
    final_report = run_config_analyst_agent(AGENT_PROMPT, config_tool)
    
    print("\n" + "=" * 50)
    print("FINAL CONFIGURATION ANALYSIS REPORT")
    print("=" * 50)
    print(final_report)
    
    # Clean up the test file
    if os.path.exists(CONFIG_FILE_NAME):
        os.remove(CONFIG_FILE_NAME)
