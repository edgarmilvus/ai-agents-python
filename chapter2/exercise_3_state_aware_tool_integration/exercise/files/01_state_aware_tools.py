import json
import re
from typing import List, Dict, Any, Optional

# --- Boilerplate Components Used ---
# ShoppingCartTool, BaseTool

# --- Agent Simulation Class ---
class ECommerceAgent:
    """Simulates the agent's interaction loop with the stateful tool."""
    def __init__(self, shopping_cart_tool: ShoppingCartTool):
        self.cart = shopping_cart_tool
        
    def process_prompt(self, prompt: str) -> str:
        """Simulates the agent deciding which tool method to call."""
        
        prompt_lower = prompt.lower()
        
        # "add ... to my cart" and "I also want ..." are the same intent, and the
        # quantity is in the sentence: parse it instead of hard-coding it.
        item_match = re.search(r"(\d+)\s*(apples?|bananas?)", prompt_lower)
        if item_match and ("add" in prompt_lower or "want" in prompt_lower):
            quantity = int(item_match.group(1))
            item = "Apple" if item_match.group(2).startswith("apple") else "Banana"
            return self.cart.add_item(item, quantity)
            
        elif "view" in prompt_lower or "what is" in prompt_lower and "cart" in prompt_lower:
            return self.cart.view_cart()
            
        elif "checkout" in prompt_lower or "ready to buy" in prompt_lower:
            return self.cart.checkout()
            
        return "I'm sorry, I couldn't understand that request."

# --- Execution Demonstration ---

print("--- Exercise 3: State-Aware Tool Integration Demo ---")

# 1. Initialize the stateful tool instance ONCE
persistent_cart = ShoppingCartTool()

# 2. Initialize the agent with the persistent instance
agent = ECommerceAgent(persistent_cart)

# Prompt 1: Add item (State: [2 Apples])
prompt1 = "Please add 2 Apples to my cart."
print(f"\nUser: {prompt1}")
response1 = agent.process_prompt(prompt1)
print(f"Agent: {response1}")
print(f"[Internal State Check: {persistent_cart.items}]")

# Prompt 2: Add another item (State: [2 Apples, 1 Banana])
prompt2 = "Now, I also want 1 Banana."
print(f"\nUser: {prompt2}")
response2 = agent.process_prompt(prompt2)
print(f"Agent: {response2}")
print(f"[Internal State Check: {persistent_cart.items}]")

# Prompt 3: Review the cart (State is maintained)
prompt3 = "What is currently in my cart?"
print(f"\nUser: {prompt3}")
response3 = agent.process_prompt(prompt3)
print(f"Agent:\n{response3}")
# Note: The agent uses the tool instance to retrieve the combined list.

# Prompt 4: Checkout (State is cleared)
prompt4 = "I'm ready to checkout."
print(f"\nUser: {prompt4}")
response4 = agent.process_prompt(prompt4)
print(f"Agent: {response4}")
print(f"[Internal State Check: {persistent_cart.items}]")
