from typing import Dict, Type, Callable

# 1. Define Custom Tool Exceptions
class AgentError(Exception): pass
class NetworkToolError(AgentError): pass
class DatabaseToolError(AgentError): pass

# 3. Create a Handler Registry
ERROR_HANDLER_REGISTRY: Dict[Type[AgentError], Callable[[str], str]] = {}

def register_handler(exception_class: Type[AgentError]):
    """Decorator to register handlers to the registry."""
    def decorator(func: Callable[[str], str]):
        ERROR_HANDLER_REGISTRY[exception_class] = func
        return func
    return decorator

# 2. Implement Tool Handlers
@register_handler(NetworkToolError)
def handle_network_error(context: str) -> str:
    """Handler for transient network issues."""
    print(f"  [HANDLER LOG] Network failure detected. Context: {context}")
    return "RECOVERY_ACTION: The network is unstable. Implement an exponential backoff retry strategy."

@register_handler(DatabaseToolError)
def handle_database_error(context: str) -> str:
    """Handler for persistent database issues."""
    print(f"  [HANDLER LOG] Database failure detected. Context: {context}")
    return "RECOVERY_ACTION: Credentials likely expired or connection misconfigured. Alert System Admin."

def simulated_tool_execution(tool_name: str):
    """Simulates tool execution and raises tool-specific errors."""
    if tool_name == "network":
        raise NetworkToolError("Timeout accessing external API.")
    elif tool_name == "db":
        raise DatabaseToolError("Authentication failed for read operation.")
    else:
        print(f"Tool {tool_name} executed successfully.")

def agent_executor_with_registry(tool_name: str):
    """4. Implements the AgentExecutor using the registry for error lookup."""
    print(f"\n--- exercise 5: Executing Tool '{tool_name}' ---")
    try:
        simulated_tool_execution(tool_name)
    except AgentError as e:
        exception_type = type(e)
        if exception_type in ERROR_HANDLER_REGISTRY:
            # Execute the registered handler function
            handler = ERROR_HANDLER_REGISTRY[exception_type]
            recovery_suggestion = handler(str(e))
            print(f"  [AGENT RESPONSE] Tool failure handled by custom registry.")
            print(f"  Suggested Agent Action: {recovery_suggestion}")
        else:
            print(f"  [AGENT RESPONSE] Unregistered error type: {exception_type.__name__}. Raising fatal error.")
            # Re-raise if no specific handler is found
            raise e

# Execution
agent_executor_with_registry("network")
agent_executor_with_registry("db")
agent_executor_with_registry("success_tool")
