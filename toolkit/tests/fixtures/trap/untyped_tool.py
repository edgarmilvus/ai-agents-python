from langchain_core.tools import tool


@tool
def search(query):
    """Find something."""
    return query
