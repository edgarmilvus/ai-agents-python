import json
from typing import List, Dict, Any, Optional

# --- Boilerplate Components Used ---
# MockLLM, MockVectorStore, ProjectRiskReflector, BaseTool
# (Assuming the boilerplate code is available in the execution environment)

class ConversationBufferWindowMemory:
    """Mock for tracking recent conversation history."""
    def __init__(self, k: int = 5):
        self.history = []
        self.k = k

    def add_message(self, speaker: str, text: str):
        self.history.append(f"{speaker}: {text}")
        if len(self.history) > self.k:
            self.history.pop(0)

    def get_history(self) -> str:
        return "\n".join(self.history)

# --- Agent Implementation ---

def project_management_agent(user_input: str, memory: ConversationBufferWindowMemory, reflector_tool: ProjectRiskReflector, llm: 'MockLLM') -> str:
    """Simulates the Project Management Agent's execution flow."""
    
    # 1. Update Memory with current input
    memory.add_message("User", user_input)
    
    current_context = memory.get_history()
    
    # 2. Conditional Tool Check (Simulated LLM Decision based on prompt)
    keywords = ["risk", "failure", "problem", "mitigation", "crisis"]
    should_reflect = any(kw in user_input.lower() for kw in keywords)
    
    tool_output = ""
    
    if should_reflect:
        print(f"\n[AGENT THOUGHT]: Risk keywords detected. Calling {reflector_tool.name} tool.")
        # The tool requires the full history for contextual search
        tool_output = reflector_tool.run(current_context)
        print(f"[TOOL OBSERVATION]: {tool_output}")
    else:
        print("[AGENT THOUGHT]: Standard query. No reflection tool needed.")

    # 3. Final Synthesis (Simulated LLM response)
    
    # The LLM synthesizes the tool output (if present) with the context.
    synthesis_prompt = f"Context:\n{current_context}\n\nTool Output (if relevant):\n{tool_output}\n\nAgent Response:"
    
    # In a real setup, the LLM would be invoked with this prompt.
    # Here, we provide a simple mock response based on whether the tool was used.
    if should_reflect:
        # The first retrieved practice is enough to ground the recommendation;
        # parsing the last line for a ':' broke whenever a document had none.
        first_practice = tool_output.splitlines()[1]
        response = (
            f"Based on the identified risk and the best practices retrieved "
            f"({first_practice}), I recommend acting on it before the next milestone."
        )
    else:
        response = f"Task status update: Task A is 80% complete. We are on track."
        
    memory.add_message("Agent", response)
    return response

# --- Execution Demonstration ---

# 1. Initialize Components
vector_store = MockVectorStore()
reflector = ProjectRiskReflector(vector_store=vector_store)
memory = ConversationBufferWindowMemory(k=5)
mock_llm = MockLLM()

print("--- Exercise 1: Project Management Agent Demo ---")

# Turn 1-3: Standard Conversation (Tool Ignored)
print("\n--- Turn 1: Status Check ---")
response1 = project_management_agent("What is the status of Task A?", memory, reflector, mock_llm)
print(f"Agent: {response1}")

print("\n--- Turn 2: Follow-up ---")
response2 = project_management_agent("Has the budget been approved?", memory, reflector, mock_llm)
print(f"Agent: {response2}")

# Turn 4: Risk-related Query (Tool Triggered)
print("\n--- Turn 3: Risk Query (Triggering Reflection) ---")
risk_query = "The team is running into dependency hell. What are the best practices for managing this risk?"
response3 = project_management_agent(risk_query, memory, reflector, mock_llm)
print(f"Agent: {response3}")

print("\n--- Final Memory State (Last 5 turns) ---")
print(memory.get_history())
