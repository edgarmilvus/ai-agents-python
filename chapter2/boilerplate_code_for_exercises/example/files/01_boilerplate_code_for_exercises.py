import json
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Mocking necessary components for demonstration
class MockLLM:
    """A simple mock LLM for testing agent logic without API calls."""
    def __init__(self, responses: Dict[str, str] = None):
        self.responses = responses if responses is not None else {}
        self.call_count = 0

    def invoke(self, prompt: str) -> str:
        self.call_count += 1
        # A caller can script this mock with substring -> response pairs.
        for trigger, response in self.responses.items():
            if trigger.lower() in prompt.lower():
                return response

        # The default scenario: a Manager Agent asking for a plan.
        if "decompose the following high-level goal" in prompt.lower():
            return json.dumps({
                "plan": [
                    {"step": 1, "action": "lookup_price", "input": {"ticker": "TSLA", "period": "1y"}, "tool": "StockPriceLookup"},
                    {"step": 2, "action": "calculate_ma", "input_from": 1, "window": 50, "tool": "CalculateMovingAverage"},
                    {"step": 3, "action": "synthesize_summary", "input_from": [1, 2], "tool": None}
                ]
            })
        
        # Default response or specific conversational response
        return f"Mock LLM Response {self.call_count} to: {prompt[:50]}..."

    def __call__(self, prompt: str) -> str:
        return self.invoke(prompt)

# --- Base Tool Structure (Adapt for LangChain/LlamaIndex as needed) ---

class BaseTool(ABC):
    """Abstract base class for custom tools."""
    name: str
    description: str

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        pass

# --- Exercise 1 Components ---

class MockVectorStore:
    """Mock for a vector store containing best practices."""
    def __init__(self):
        self.documents = [
            ("Scope creep mitigation strategies", "Always define scope clearly and use change requests."),
            ("Handling stakeholder conflicts", "Establish clear communication channels and decision matrices."),
            ("Budget overrun warning signs", "Monitor burn rate daily and forecast remaining runway weekly.")
        ]
    
    def similarity_search(self, query: str, k: int = 2) -> List[str]:
        # Simple keyword matching simulation for mock retrieval
        if "risk" in query.lower() or "failure" in query.lower():
            # Returns relevant documents based on risk keywords
            return [doc[1] for doc in self.documents[:k]]
        return ["No relevant best practice found for this query."]

class ProjectRiskReflector(BaseTool):
    name = "ProjectRiskReflector"
    description = "Use this tool ONLY when the user asks about project risk, failure, or strategic mitigation. Input must be the full conversation history."
    
    def __init__(self, vector_store: MockVectorStore):
        self.vector_store = vector_store

    def run(self, conversation_history: str) -> str:
        retrieved_docs = self.vector_store.similarity_search(conversation_history)
        return "Retrieved Best Practices:\n" + "\n".join(retrieved_docs)

# --- Exercise 2 Components ---

class StockPriceLookup(BaseTool):
    name = "StockPriceLookup"
    description = "Looks up historical stock price data for a given ticker and period."

    def run(self, ticker: str, period: str) -> str:
        if ticker == "TSLA" and period == "1y":
            # Mocking complex data output
            return json.dumps({"ticker": ticker, "data_points": 250, "sample_prices": [150.0, 155.5, 160.2]})
        return f"Could not find data for {ticker}."

class CalculateMovingAverage(BaseTool):
    name = "CalculateMovingAverage"
    description = "Calculates the X-day moving average based on price data provided as input."

    def run(self, price_data_json: str, window: int) -> str:
        try:
            data = json.loads(price_data_json)
            # Simplified mock calculation
            avg = sum(data['sample_prices']) / len(data['sample_prices'])
            return f"The {window}-day moving average for {data['ticker']} is approximately ${avg:.2f}."
        except Exception:
            return "Error calculating moving average: Invalid data format."

# --- Exercise 3 Components ---

class ShoppingCartTool(BaseTool):
    name = "ShoppingCartTool"
    description = "Manages the user's shopping cart state. Use add_item, view_cart, and checkout."
    
    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def add_item(self, item_name: str, quantity: int) -> str:
        """Adds an item and quantity to the persistent cart."""
        self.items.append({"name": item_name, "quantity": quantity})
        return f"Added {quantity} x {item_name} to the cart."

    def view_cart(self) -> str:
        """Returns a string summary of all items currently in the cart."""
        if not self.items:
            return "The shopping cart is currently empty."
        
        summary = ["Current Cart Contents:"]
        for item in self.items:
            summary.append(f"- {item['quantity']} x {item['name']}")
        return "\n".join(summary)

    def checkout(self) -> str:
        """Finalizes the order and clears the cart state."""
        total_items = sum(item['quantity'] for item in self.items)
        if total_items == 0:
            return "Cannot checkout. The cart is empty."
        
        self.items = [] # Critical: State reset
        return f"Order successfully placed for {total_items} items. Cart cleared."

    def run(self, action: str, **kwargs) -> str:
        """Dispatches the agent's chosen action to the matching method.

        BaseTool declares run() abstract, so a subclass that does not implement
        it cannot even be instantiated; this is also the single entry point a
        real framework would expose to the model.
        """
        if action == "add_item":
            return self.add_item(**kwargs)
        if action == "view_cart":
            return self.view_cart()
        if action == "checkout":
            return self.checkout()
        raise ValueError(f"Unknown cart action: {action}")

# --- Exercise 4 Components ---

class PlanStepCounter(BaseTool):
    name = "PlanStepCounter"
    description = "Analyzes a proposed plan string and returns the number of distinct steps found. Input must be the raw plan text."

    def run(self, plan_text: str) -> int:
        """Counts the number of steps, assuming steps are delimited by newlines or numbered lists."""
        lines = plan_text.strip().split('\n')
        # A simple heuristic: count lines starting with a number or bullet point
        step_count = sum(1 for line in lines if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '*')))
        
        # If the plan is very complex, force a high count to trigger correction
        if "Research three different investment strategies" in plan_text:
             return 6 # Artificially high count to force failure
        
        return max(1, step_count) # Ensure minimum count is 1
