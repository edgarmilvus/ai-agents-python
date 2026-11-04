from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END

# 1. State Definition (Expanded)
class FinancialState(TypedDict):
    stock_symbol: str
    raw_data: List[str]
    report_draft: str
    review_feedback: Optional[str]
    is_volatile: bool # NEW
    risk_section_added: bool # NEW

# 2. Node Implementations (Focus on new nodes and routing)

def research_node(state: FinancialState) -> Dict[str, Any]:
    symbol = state["stock_symbol"]
    data = [f"Price: $150", f"Volume: 10M"]
    print(f"--- Research: Gathered data for {symbol}.")
    return {"raw_data": data}

def drafting_node(state: FinancialState) -> Dict[str, Any]:
    """Generates the initial report draft."""
    draft = f"Financial Report for {state['stock_symbol']}:\n\n1. Market Overview: The outlook is positive."
    print("--- Drafting: Initial report generated.")
    return {"report_draft": draft, "risk_section_added": False}

def volatility_checker_node(state: FinancialState) -> Dict[str, Any]:
    """Checks stock volatility (simulated)."""
    symbol = state["stock_symbol"]
    
    # Simulation: TSLA is volatile, AAPL is not.
    is_volatile = (symbol == "TSLA")
    
    print(f"--- Checker: Volatility check for {symbol}. Result: {is_volatile}")
    return {"is_volatile": is_volatile}

def risk_drafter_node(state: FinancialState) -> Dict[str, Any]:
    """Specialized node to add the risk mitigation section."""
    draft = state["report_draft"]
    
    risk_section = "\n\n2. Risk Mitigation Strategy (MANDATORY ADDITION):\nThe stock exhibits high volatility. We recommend a stop-loss order."
    
    new_draft = draft + risk_section
    print("--- Risk Drafter: Added mandatory risk section.")
    
    return {
        "report_draft": new_draft,
        "risk_section_added": True
    }

def review_node(state: FinancialState) -> Dict[str, Any]:
    """Simulates the review process."""
    print(f"--- Review: Checking report structure.")
    return {"review_feedback": "PASS"}

def finalize_node(state: FinancialState) -> None:
    """Finalizes the report."""
    print("--- Finalize: Report is complete.")
    return {}

# 3. Conditional Routing Function (from volatility_checker_node)
def route_on_volatility(state: FinancialState) -> str:
    is_volatile = state["is_volatile"]
    risk_added = state["risk_section_added"]
    
    if is_volatile and not risk_added:
        return "risk_drafter_node"
    else:
        return "review_node"

# 4. Build the Graph
workflow = StateGraph(FinancialState)

workflow.add_node("research_node", research_node)
workflow.add_node("drafting_node", drafting_node)
workflow.add_node("volatility_checker_node", volatility_checker_node)
workflow.add_node("risk_drafter_node", risk_drafter_node)
workflow.add_node("review_node", review_node)
workflow.add_node("finalize_node", finalize_node)

workflow.set_entry_point("research_node")

workflow.add_edge("research_node", "drafting_node")
workflow.add_edge("drafting_node", "volatility_checker_node")

# Conditional Edge for the new cycle
workflow.add_conditional_edges(
    "volatility_checker_node",
    route_on_volatility,
    {
        "risk_drafter_node": "risk_drafter_node",
        "review_node": "review_node"
    }
)

# After drafting the risk section, proceed to review
workflow.add_edge("risk_drafter_node", "review_node")

workflow.add_edge("review_node", "finalize_node")
workflow.add_edge("finalize_node", END)

app_844 = workflow.compile()

# Example Execution: Volatile Stock (TSLA)
volatile_input = {
    "stock_symbol": "TSLA", "raw_data": [], "report_draft": "",
    "is_volatile": False, "risk_section_added": False, "review_feedback": None
}
print("--- Starting Agent for Volatile Stock (TSLA) ---")
app_844.invoke(volatile_input)
