import textwrap

# --- Setup for Agent B (ReAct) ---
def search_web(query: str) -> str:
    """Simulates a search tool returning current, dynamic data."""
    if "current market capitalization of Apple" in query:
        return "Observation: Apple Inc. Market Cap (Current): $2.95 Trillion."
    if "current market capitalization of Microsoft" in query:
        return "Observation: Microsoft Corp. Market Cap (Current): $3.15 Trillion."
    return "Observation: Search failed."

# 1. Agent A: Pure CoT Agent (No Tools)
print("--- 1. Agent A: Pure CoT (Internal Knowledge) ---")

cot_prompt = textwrap.dedent("""
Based purely on your internal knowledge cutoff date, which company, Apple or Microsoft, has the higher market capitalization, and why?
Use a detailed Chain-of-Thought structure to justify your answer. Explicitly state your knowledge cutoff date.
""")

# Simulation of LLM trained on data before Microsoft's recent surge
cot_llm_output = textwrap.dedent("""
---CoT Reasoning---

1. **Knowledge Cutoff:** My training data cutoff is January 2023.
2. **Historical Data:** As of late 2022/early 2023, Apple consistently held the highest market capitalization, often fluctuating between $2.5T and $3.0T. Microsoft was typically slightly behind, often around $2.0T to $2.5T.
3. **Internal Comparison:** Based on this historical trend, Apple is internally weighted as the higher-cap company.
---Conclusion---
Answer: Based on my internal knowledge cutoff (Jan 2023), **Apple** has the higher market capitalization. The reasoning is based on its consistent historical lead in the period preceding my training data cutoff.
""")
print(cot_llm_output)


# 2. Agent B: ReAct Agent (With Search Tool)
print("\n--- 2. Agent B: ReAct (External Tool Use) ---")

react_prompt = textwrap.dedent("""
You must determine which company, Apple or Microsoft, has the higher market capitalization.
You MUST use the 'search_web(query)' tool to obtain the most current data before answering.
Follow the Thought/Action/Observation pattern.
""")

# Simulation of ReAct Trace
react_trace = []

# Step 1: Check Apple
react_trace.append("Thought: I need to find the current market cap of Apple.")
react_trace.append("Action: search_web('current market capitalization of Apple')")
obs_apple = search_web("current market capitalization of Apple")
react_trace.append(obs_apple) # Apple: $2.95 Trillion

# Step 2: Check Microsoft
react_trace.append("Thought: Now I need the current market cap of Microsoft for comparison.")
react_trace.append("Action: search_web('current market capitalization of Microsoft')")
obs_microsoft = search_web("current market capitalization of Microsoft")
react_trace.append(obs_microsoft) # Microsoft: $3.15 Trillion

# Step 3: Synthesis and Final Answer
react_trace.append("Thought: Apple's cap is $2.95T and Microsoft's cap is $3.15T. Microsoft is currently higher.")
react_trace.append("Answer: Based on the current observed data, **Microsoft** has the higher market capitalization ($3.15 Trillion) compared to Apple ($2.95 Trillion).")

print("\n".join(react_trace))

# 3. Comparative Analysis
print("\n--- 3. Comparative Analysis ---")
analysis = textwrap.dedent("""
The ReAct agent (Agent B) is demonstrably superior for dynamic, fact-based queries. Agent A, relying on pure CoT, provided an answer based on outdated historical data (Apple), leading to a factual error (a form of hallucination in a dynamic context). Agent B, however, utilized the iterative ReAct pattern: it planned two search Actions, received two external Observations containing current market data, and then used that verified data to synthesize the correct final Answer (Microsoft). The crucial Observation step in the ReAct loop prevents the LLM from relying on its internal, stale weights, ensuring accuracy for real-time information.
""")
print(analysis)
