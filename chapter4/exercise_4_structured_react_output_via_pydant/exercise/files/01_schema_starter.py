from pydantic import BaseModel, Field
import json
from typing import List

# 1. Define Pydantic Output Schema
class ResearchSummary(BaseModel):
    """
    A structured summary of the agent's research findings after completing the ReAct loop.
    """
    topic: str = Field(description="The original topic researched by the agent.")
    key_findings: List[str] = Field(description="3-5 critical bullet points summarizing the results.")
    confidence_score: int = Field(description="Agent's confidence (1-100) in the data quality.")
    tools_used: int = Field(description="Total count of tools executed during the research process.")

# 2. Conceptual Integration (Illustrating the requirement)

# --- Simulation Setup ---
# Assume the ReAct loop has successfully executed 3 tool calls and gathered data.
# The final prompt to the LLM (after the ReAct trace is complete) must instruct it
# to format the final answer based on the schema.

def generate_structured_final_answer(agent_trace: List[str], research_topic: str, tool_count: int) -> dict:
    """
    Conceptual function representing the final step of the ReAct agent, 
    where the LLM is prompted to structure its findings.
    """
    
    # In a real implementation, the LLM would see the full trace history 
    # and the Pydantic schema definition, then generate the JSON output.
    
    # Example Prompt Fragment (inserted after the last Observation):
    # "Based on the preceding Thought/Action/Observation history, summarize your 
    # findings for the topic '{research_topic}' into the following JSON schema."
    
    # Mock LLM Output (what the LLM must generate):
    mock_json_output = {
        "topic": research_topic,
        "key_findings": [
            "Increased compliance costs for SMEs are projected.",
            "The definition of 'high-risk AI' remains a primary point of contention.",
            "Adoption rates vary significantly across member states."
        ],
        "confidence_score": 88,
        "tools_used": tool_count
    }
    
    # 3. Verification Step
    try:
        # Attempt to validate the mock output against the schema
        summary_instance = ResearchSummary(**mock_json_output)
        print("--- Pydantic Validation Successful ---")
        print(summary_instance.model_dump_json(indent=2))
        return summary_instance.model_dump()
    except Exception as e:
        print(f"Validation Failed: {e}")
        raise

# Example execution:
# generate_structured_final_answer(agent_trace=[], research_topic="EU AI Act Impact", tool_count=3)
