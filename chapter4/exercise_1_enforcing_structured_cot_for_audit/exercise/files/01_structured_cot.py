import textwrap

# 1. Define the Custom Prompt Template
def create_structured_cot_prompt(input_scenario: str) -> str:
    """
    Creates a system prompt designed to enforce a strict, auditable Chain-of-Thought structure.
    """
    system_instruction = textwrap.dedent("""
    You are an expert logistics and financial analyst. Your task is to evaluate three candidate warehouse locations (A, B, C) based on three weighted criteria.
    You MUST structure your entire response using the exact section headers provided below. Do not deviate from this format.

    ---INPUT DATA---
    {scenario}
    ---END INPUT DATA---

    ---ASSUMPTIONS---
    [Placeholder for assumptions, e.g., weighting of criteria]
    
    ---STEP 1: Material Analysis---
    [Evaluate locations based on raw material proximity only]
    
    ---STEP 2: Logistics Analysis---
    [Evaluate locations based on major transport hubs only]
    
    ---STEP 3: Financial Analysis---
    [Evaluate locations based on local tax incentives only]
    
    ---SYNTHESIS & CONCLUSION---
    [Combine all three analyses, state the final recommended location, and provide a justification score out of 100.]
    """)
    return system_instruction.format(scenario=input_scenario)

# 2. Input Data Simulation
input_data = textwrap.dedent("""
Locations:
A: Materials (High), Transport (Low), Tax (Medium)
B: Materials (Medium), Transport (High), Tax (Low)
C: Materials (Low), Transport (Medium), Tax (High)
Weighting: Materials (40%), Transport (35%), Tax (25%)
""")

# 3. Execution (Simulated LLM Output)
prompt = create_structured_cot_prompt(input_data)
# print(prompt) # Print the prompt to verify instructions

# Simulation of the LLM's response adhering to the structure:
simulated_llm_output = textwrap.dedent(f"""
---ASSUMPTIONS---

1. The provided weighting is strictly adhered to: Materials (40%), Transport (35%), Tax (25%).
2. High = 10 points, Medium = 5 points, Low = 2 points for scoring.

---STEP 1: Material Analysis---
Location A scores 10 points (40% weight). Weighted score: 4.0
Location B scores 5 points (40% weight). Weighted score: 2.0
Location C scores 2 points (40% weight). Weighted score: 0.8
(A is the strongest here.)

---STEP 2: Logistics Analysis---
Location A scores 2 points (35% weight). Weighted score: 0.7
Location B scores 10 points (35% weight). Weighted score: 3.5
Location C scores 5 points (35% weight). Weighted score: 1.75
(B is the strongest here.)

---STEP 3: Financial Analysis---
Location A scores 5 points (25% weight). Weighted score: 1.25
Location B scores 2 points (25% weight). Weighted score: 0.5
Location C scores 10 points (25% weight). Weighted score: 2.5
(C is the strongest here.)

---SYNTHESIS & CONCLUSION---
Total Scores:
A: 4.0 + 0.7 + 1.25 = 5.95
B: 2.0 + 3.5 + 0.5 = 6.0
C: 0.8 + 1.75 + 2.5 = 5.05

The final recommended location is **Location B**. It achieves the highest balance, narrowly edging out Location A by maximizing the critical Transport hub weighting (35%) while maintaining a medium Material score.
Justification Score: 60/100 (based on the 6.0 weighted score out of a theoretical maximum of 10.0, scaled to 100).
""")

print("--- Simulated Structured CoT Output ---")
print(simulated_llm_output)
