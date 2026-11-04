import os
from crewai import Agent, Task, Crew, Process

# --- Exercise Setup ---
# All exercises assume the necessary API keys are set in the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

# The configuration the four exercises share. The `openai/` prefix selects the
# OpenAI-compatible provider; `base_url` points it at the gateway.
llm_config = {
    "model": f"openai/{MODEL}",
    "base_url": BASE_URL,
    "api_key": os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    "temperature": 0.2,
}
