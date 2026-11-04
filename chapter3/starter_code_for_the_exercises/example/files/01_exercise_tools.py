import hashlib
from typing import Any, Optional

# --- Tool Implementations for Exercises 1, 4, and 5 ---

# Exercise 1 Tools (File I/O)
def read_json_config(file_path: str) -> str:
    """
    Reads the full content of a specified JSON configuration file. 
    Returns the content as a string or an error message if the file is not found.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return json.dumps(data, indent=4)
    except FileNotFoundError:
        return f"ERROR: Configuration file not found at path: {file_path}"
    except json.JSONDecodeError:
        return f"ERROR: File at {file_path} is not valid JSON."

def update_json_config(file_path: str, key: str, value: Any) -> str:
    """
    Updates a single key-value pair in a JSON configuration file. 
    The value must be a basic type (string, number, boolean) or a valid JSON structure.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize with empty dict if file is missing or corrupt
        data = {} 
        
    try:
        # Attempt to parse value if it looks like a JSON string, otherwise use raw input
        if isinstance(value, str):
            try:
                # Try to load complex structures if the LLM provided them as strings
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value
        else:
            parsed_value = value

        data[key] = parsed_value
        
        # Write back the updated data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return f"SUCCESS: Configuration key '{key}' updated successfully. New value: {data[key]}"
    except TypeError as e:
        return f"ERROR: Failed to serialize data. Value type is invalid for JSON: {e}"
    except Exception as e:
        return f"CRITICAL ERROR during update: {e}"

# Exercise 2 Tool (API Integration)
def get_stock_price(ticker_symbol: str) -> str:
    """
    Fetches the real-time stock price for a single ticker symbol using the external financial API. 
    Requires the exact ticker symbol (e.g., GOOGL).
    """
    result = MockFinancialAPI.fetch_stock_price(ticker_symbol)
    
    if result.get("status") == "error":
        return f"API ERROR: Could not retrieve price for {ticker_symbol}. Message: {result['message']}"
    
    data = result.get("data", {})
    price = data.get("price")
    updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("last_updated")))
    
    return f"The current price for {ticker_symbol.upper()} is ${price:.2f}, last updated at {updated}."

# Exercise 3 Tool (Database/ORM)
def query_inventory(category: Optional[str] = None, min_price: Optional[float] = None, max_quantity: Optional[int] = None) -> str:
    """
    Queries the product inventory database using ORM filtering based on optional constraints. 
    Returns a JSON list of matching items or a failure message.
    """
    session = Session()
    try:
        query = session.query(InventoryItem)
        
        if category:
            query = query.filter(InventoryItem.category == category)
        if min_price is not None:
            query = query.filter(InventoryItem.price >= min_price)
        if max_quantity is not None:
            query = query.filter(InventoryItem.quantity <= max_quantity)
            
        results = query.all()
        
        if not results:
            return "No inventory items matched the specified criteria."
            
        item_list = [item.to_dict() for item in results]
        return json.dumps(item_list, indent=4)
        
    except Exception as e:
        return f"DATABASE QUERY ERROR: Failed to execute query due to internal error: {e}"
    finally:
        session.close()

# Exercise 4 Tools (Orchestration Challenge)
def check_live_service_status(service_name: str) -> str:
    """
    Checks the real-time, current operational status of a specific internal microservice 
    (e.g., 'deployment_api', 'log_aggregator').
    """
    status = MockFinancialAPI.get_service_status(service_name)
    return f"Current status of the '{service_name}' service is: {status}."

def analyze_deployment_log(log_path: str) -> str:
    """
    Reads the historical deployment log file, summarizes error counts, and extracts the last critical error. 
    Use this tool for historical context and failure analysis.
    """
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        error_count = 0
        last_error = "N/A"
        
        for line in reversed(lines):
            if "ERROR" in line:
                error_count += 1
                if last_error == "N/A":
                    last_error = line.strip()
            
        return (f"Log analysis complete: Total lines analyzed = {total_lines}. "
                f"Total ERROR entries found = {error_count}. "
                f"Last critical error logged: {last_error}.")

    except FileNotFoundError:
        return f"ERROR: Log file not found at path: {log_path}"

# Exercise 5 Tool (Validation/Robustness)
def calculate_hash(data: str, algorithm: str) -> str:
    """
    Calculates the cryptographic hash digest for input data using a supported algorithm (sha256 or md5).
    """
    SUPPORTED_ALGORITHMS = ["sha256", "md5"]
    MAX_DATA_SIZE = 1024 # characters
    
    if algorithm.lower() not in SUPPORTED_ALGORITHMS:
        return f"VALIDATION ERROR: Algorithm '{algorithm}' is not supported. Please use one of: {', '.join(SUPPORTED_ALGORITHMS)}."
        
    if len(data) > MAX_DATA_SIZE:
        return f"VALIDATION ERROR: Input data exceeds the maximum allowed size of {MAX_DATA_SIZE} characters. Length provided: {len(data)}."

    try:
        h = hashlib.new(algorithm.lower())
        h.update(data.encode('utf-8'))
        return f"Hash ({algorithm}): {h.hexdigest()}"
    except Exception as e:
        return f"CRITICAL HASHING ERROR: An unexpected error occurred during calculation: {e}"
