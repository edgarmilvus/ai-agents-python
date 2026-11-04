import re

# --- Exercise 3: Rule-Based Tool Routing and Execution ---

# 1. Define Mock Tools
def financial_calculator(expression):
    """Mock tool for calculating math."""
    # A tool that evals whatever text reached it is an execution hole, so the
    # expression is checked before it is evaluated: digits, operators, spaces.
    if not re.fullmatch(r"[0-9+\-*/(). ]+", str(expression)):
        return "Calculation Tool Error: Invalid expression."
    try:
        result = eval(str(expression))
        return f"Calculation Tool Result: The result of {expression} is {result}."
    except Exception:
        return "Calculation Tool Error: Invalid expression."

def weather_api_lookup(city):
    """Mock tool for looking up weather."""
    if 'london' in city.lower():
        return f"Weather Tool Result: Current weather in {city}: 15°C and cloudy."
    return f"Weather Tool Result: Cannot find current weather data for {city}."

def database_query(query_string):
    """Mock tool for database retrieval."""
    if 'user data' in query_string.lower():
        return "DB Tool Result: Retrieved 1,500 records of user data from the main table."
    return "DB Tool Result: Query executed, but no specific data found."

# 2. Tool Manifest (Mapping keywords to functions)
TOOL_MANIFEST = {
    'calculate': financial_calculator,
    'weather': weather_api_lookup,
    'database': database_query
}

# Words the routing layer accepts in place of an operator
OPERATOR_WORDS = (
    ('multiplied by', '*'),
    ('divided by', '/'),
    ('times', '*'),
    ('plus', '+'),
    ('minus', '-'),
)

def route_query(query):
    """
    The Decide phase: Routes the query to the appropriate tool and extracts args.
    """
    query_lower = query.lower()
    
    if 'calculate' in query_lower or 'math' in query_lower:
        # Rewrite the operator words, then keep the arithmetic run. Splitting on
        # spaces and gluing the last three tokens together turns "5 times 12"
        # into "5times12", which is not an expression.
        expression = query_lower
        for word, operator in OPERATOR_WORDS:
            expression = expression.replace(word, operator)
        match = re.search(r"[0-9.][0-9.+\-*/() ]*", expression)
        if match:
            return 'calculate', match.group(0).strip()
        return 'calculate', '1+1' # Default if extraction fails
            
    elif 'weather' in query_lower or 'forecast' in query_lower:
        # Extract the city that follows the preposition "in". A word boundary
        # keeps the "in" of "Berlin" from splitting the city name.
        match = re.search(r"\bin\s+([A-Za-z][A-Za-z .'-]*)", query)
        if match:
            city = match.group(1).strip()
            return 'weather', city
        return 'weather', 'default city'
        
    elif 'database' in query_lower or 'retrieve' in query_lower:
        # Simple argument extraction for database
        return 'database', query
        
    return None, None

def execute_tool(tool_name, args):
    """
    The Act phase: Dynamically calls the selected tool.
    """
    if tool_name and tool_name in TOOL_MANIFEST:
        tool_function = TOOL_MANIFEST[tool_name]
        print(f"[Act] Invoking Tool: {tool_name} with arguments: '{args}'")
        
        # Handle tuple vs single argument call
        if isinstance(args, tuple):
            result = tool_function(*args)
        else:
            result = tool_function(args)
            
        return result
    else:
        return "Agent Decision: No appropriate tool found for this query."

def run_tool_router_agent(query):
    print(f"\n--- Processing Query: '{query}' ---")
    
    # Decide (Route)
    tool_name, args = route_query(query)
    
    # Act (Execute)
    result = execute_tool(tool_name, args)
    
    print(f"--- Final Agent Response ---\n{result}")
    return result


if __name__ == "__main__":
    run_tool_router_agent("I need to calculate 5 times 12")
    run_tool_router_agent("What is the weather in London?")
    run_tool_router_agent("Retrieve user data from the database.")
    run_tool_router_agent("Tell me a joke.") # Should fail to route
