from langchain_core.tools import tool


@tool
def search(query: str) -> str:
    """Find something."""
    return query


def run(prompt: str) -> str:
    return prompt
