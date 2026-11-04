#!/usr/bin/env python3
# -*- coding coding: utf-8 -*-

import configparser
from typing import Type
from pydantic import BaseModel, Field

# --- 1. Tool Input Schema Definition ---
# This helps the LLM structure its arguments for the tool call
class ConfigReadInput(BaseModel):
    """Input schema for the ConfigFileReaderTool."""
    section: str = Field(description="The section header in the INI file (e.g., 'SYSTEM').")
    key: str = Field(description="The specific configuration key to retrieve (e.g., 'LOG_LEVEL').")

# --- 2. Custom Tool Implementation ---
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

    def _run(self, section: str, key: str) -> str:
        """Reads the configuration file."""
        config = configparser.ConfigParser()
        
        # In a real scenario, handle file existence carefully
        try:
            # Assume app_config.ini is created and accessible
            config.read('app_config.ini')
        except Exception as e:
            return f"Error: Could not read configuration file. {e}"

        if section not in config:
            return f"Error: Configuration section '{section}' not found."
        
        if key not in config[section]:
            return f"Error: Key '{key}' not found in section '{section}'."

        return f"Configuration Value: {section}.{key} = {config[section][key]}"

    # Note: Depending on the framework (e.g., LangChain), the method 
    # signature might be slightly different (e.g., a single 'run' method 
    # accepting kwargs, or a direct call method). The core logic remains the same.


# Example of how the tool would be used by the agent framework:
# tool_instance = ConfigFileReaderTool()
# tool_instance._run(section="SYSTEM", key="LOG_LEVEL") 
# -> Output: "Configuration Value: SYSTEM.LOG_LEVEL = INFO"
