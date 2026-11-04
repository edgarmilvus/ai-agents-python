# exercise_2_dynamic_structured_agent.py

import json
from typing import List, Type
from pydantic import BaseModel, Field, ValidationError

# --- 1. Structured Output Schema ---

class ResearchReport(BaseModel):
    """
    A structured report containing research findings based on specific temporal constraints.
    """
    query: str = Field(description="The original topic provided for research.")
    cutoff_date_used: str = Field(description="The date used to filter sources (YYYY-MM-DD).")
    summary: str = Field(description="A concise summary of findings, strictly adhering to the cutoff date. Must be approximately 300 words.")
    source_count: int = Field(description="Total number of unique, relevant sources found and cited.")
    key_insights: List[str] = Field(description="3 to 5 critical takeaways from the research.")

# --- 2. Dynamic Prompt Template ---

def create_dynamic_prompt(topic: str, cutoff_date: str) -> str:
    """Generates a highly specific prompt integrating dynamic constraints."""
    
    prompt_template = f"""
    Perform deep research on the following topic: "{topic}".
    
    **CRITICAL CONSTRAINT:** You must strictly limit your findings to information 
    published on or after the specific date: {cutoff_date}. 
    Discard and ignore any source or data point published before this date. 
    
    Your final output MUST be a JSON object that strictly conforms to the provided 
    Pydantic schema (ResearchReport).
    """
    return prompt_template.strip()

# --- 3. Mock Execution Function (Simulating LLM + Structured Output Enforcement) ---

def mock_llm_call_with_pydantic(prompt: str) -> str:
    """
    Simulates an LLM call designed to produce Pydantic-compliant JSON output.
    """
    print(f"--- Simulating LLM Execution ---")
    
    # Extract dynamic inputs from the prompt for the mock output
    topic = prompt.split('"')[1]
    date = prompt.split('date: ')[1].split('.')[0].strip()
    
    # Create the mock output that adheres precisely to the ResearchReport schema
    mock_data = ResearchReport(
        query=topic,
        cutoff_date_used=date,
        summary=(
            "Research conducted strictly post-2021 shows a significant shift towards "
            "decentralized clinical trials (DCTs). Regulatory bodies, including the FDA, "
            "have issued clearer guidance since 2021, accelerating adoption. The use of "
            "wearable technology and remote patient monitoring has become standard, "
            "drastically reducing site visits. This trend is driven by improved patient "
            "recruitment and retention rates, especially in rare disease studies. "
            "However, challenges remain regarding data standardization and cybersecurity "
            "across diverse platforms, which are the main focus of recent 2023/2024 publications."
        ),
        source_count=18,
        key_insights=[
            "Regulatory clarity post-2021 boosted DCT adoption.",
            "Wearable tech integration is now a baseline requirement.",
            "Patient retention rates improved by an average of 15% in DCTs.",
            "Cybersecurity concerns are the primary barrier to broader implementation."
        ]
    )
    
    # Return the JSON string output
    return mock_data.model_dump_json(indent=2)


def run_dynamic_research_query(topic: str, cutoff_date: str) -> str:
    """
    Configures and executes the agent task with dynamic inputs and structured output enforcement.
    """
    
    # 1. Generate the dynamic prompt
    prompt = create_dynamic_prompt(topic, cutoff_date)
    print(f"Generated Prompt (Snippet):\n{prompt[:150]}...\n")
    
    # 2. Execute the agent (simulated)
    raw_json_output = mock_llm_call_with_pydantic(prompt)
    
    # 3. Validation and Parsing
    try:
        # Attempt to parse the raw output into the Pydantic model
        validated_report = ResearchReport.model_validate_json(raw_json_output)
        print("\n[SUCCESS] Output successfully validated against ResearchReport schema.")
        
        # Return the clean, validated JSON string
        return validated_report.model_dump_json(indent=2)
        
    except ValidationError as e:
        print("\n[ERROR] Agent failed to produce valid structured output!")
        print(f"Validation Error Details: {e}")
        return "Validation Failed."

# --- Execution and Validation ---
if __name__ == "__main__":
    
    RESEARCH_TOPIC = "Impact of AI on Decentralized Clinical Trials"
    CUTOFF_DATE = "2021-01-01"

    final_structured_output = run_dynamic_research_query(
        topic=RESEARCH_TOPIC,
        cutoff_date=CUTOFF_DATE
    )
    
    print("\n" + "=" * 50)
    print(f"FINAL STRUCTURED REPORT (for {RESEARCH_TOPIC})")
    print("=" * 50)
    print(final_structured_output)
    
    # Final check
    if final_structured_output != "Validation Failed.":
        data = json.loads(final_structured_output)
        print(f"\n[Validation Check] Cutoff date '{data['cutoff_date_used']}' successfully integrated and validated.")
