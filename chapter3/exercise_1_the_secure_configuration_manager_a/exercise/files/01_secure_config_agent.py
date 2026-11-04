import json
import os
from typing import Any, Dict

# Assume CONFIG_FILE_PATH is defined from the setup: "agent_config.json"

def read_json_config(file_path: str) -> str:
    """
    Reads the full content of a specified JSON configuration file. 
    Returns the content as a string or an error message if the file is not found or invalid.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Return formatted JSON string for easy LLM parsing
            return json.dumps(data, indent=4)
    except FileNotFoundError:
        return f"ERROR: Configuration file not found at path: {file_path}"
    except json.JSONDecodeError:
        return f"ERROR: File at {file_path} is not valid JSON."

def update_json_config(file_path: str, key: str, value: Any) -> str:
    """
    Updates a single key-value pair in a JSON configuration file. 
    The tool ensures the resulting structure remains valid JSON.
    """
    data: Dict[str, Any] = {}
    
    # 1. Load existing data, handle missing/corrupt file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty dictionary
        data = {} 
    except json.JSONDecodeError:
        # If file is corrupt, log and start fresh (or handle as needed)
        return f"ERROR: Existing file at {file_path} is corrupt. Cannot safely update."
        
    # 2. Prepare the value
    parsed_value = value
    if isinstance(value, str):
        try:
            # Attempt to parse the string value if it represents a JSON structure (e.g., list, dict)
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # If it's just a regular string, use it as is
            parsed_value = value

    # 3. Update data
    data[key] = parsed_value
    
    # 4. Validation and Write back
    try:
        # Check if the whole structure is serializable before writing
        json.dumps(data) 
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return f"SUCCESS: Configuration key '{key}' updated successfully. New value: {data[key]}"
    except TypeError as e:
        # Catches non-serializable objects (like functions or class instances)
        return f"ERROR: Failed to update configuration. The value provided is not a valid JSON serializable type: {e}"
    except Exception as e:
        return f"CRITICAL ERROR during file write: {e}"

# --- Agent Prompting Strategy ---
# System Prompt Snippet:
# "You are the Config Auditor Agent. Your primary function is to manage JSON configuration files 
# using the provided tools. Always prioritize using `read_json_config` before answering questions 
# about current settings. When modifying a setting, use `update_json_config` and then confirm 
# the change by reading the file again."
#
# Challenge 1: "What is the current max_retries setting?"
# Agent should call: read_json_config(file_path="agent_config.json")
#
# Challenge 2: "Change the agent_name to 'Configuration_Bot' and report the full configuration back to me."
# Agent should call 1: update_json_config(file_path="agent_config.json", key="agent_name", value="Configuration_Bot")
# Agent should call 2: read_json_config(file_path="agent_config.json")
