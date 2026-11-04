from typing import List, Dict, Any, Optional
# Assume InventoryItem, Session, and necessary SQLAlchemy components are defined from the setup

def query_inventory(category: Optional[str] = None, min_price: Optional[float] = None, max_quantity: Optional[int] = None) -> str:
    """
    Queries the product inventory database using ORM filtering based on optional constraints: 
    category, minimum price, and maximum quantity. 
    Returns a JSON list of matching items or a failure message.
    """
    session = Session()
    try:
        query = session.query(InventoryItem)
        
        # Dynamic Filtering Logic
        if category:
            query = query.filter(InventoryItem.category == category)
        if min_price is not None:
            # Note: LLM must provide a float for min_price
            query = query.filter(InventoryItem.price >= min_price)
        if max_quantity is not None:
            # Note: LLM must provide an integer for max_quantity
            query = query.filter(InventoryItem.quantity <= max_quantity)
            
        results = query.all()
        
        if not results:
            return "No inventory items matched the specified criteria."
            
        # Convert results to a list of dictionaries for JSON serialization
        item_list = [item.to_dict() for item in results]
        return json.dumps(item_list, indent=4)
        
    except Exception as e:
        # Catch potential database connection issues or malformed parameters
        return f"DATABASE QUERY ERROR: Failed to execute query due to internal error: {e}"
    finally:
        # Crucial step: ensure the session is closed
        session.close()

# --- Agent Prompting Challenge Strategy ---
# Query: "I need a list of all items categorized as 'Electronics' that cost more than $500. 
# Then, tell me how many items are in the 'Peripherals' category."
#
# Agent Execution Sequence (Simulated):
# 1. Tool Call (Electronics + Price Filter): 
#    query_inventory(category="Electronics", min_price=500.0)
#    Output: JSON list containing 'Laptop Pro X' and '4K Monitor 32''
#
# 2. Tool Call (Peripherals Category Count):
#    query_inventory(category="Peripherals")
#    Output: JSON list containing 'Mechanical Keyboard' and 'Ergonomic Mouse'
#
# LLM Synthesis:
# "The items categorized as Electronics costing over $500 are: [list items]. 
# The Peripherals category currently contains 2 distinct items."
