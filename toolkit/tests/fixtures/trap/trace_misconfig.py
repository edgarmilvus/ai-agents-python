import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"


def traced():
    return "run"
