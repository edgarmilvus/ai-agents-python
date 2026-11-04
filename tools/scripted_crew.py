"""Shared pieces for the chapter 7 harnesses: a scripted CrewAI model."""
import os
import sys
import warnings
from pathlib import Path

warnings.simplefilter("ignore")

import crewai
from crewai.llms.base_llm import BaseLLM

CALLS = []


class ScriptedLLM(BaseLLM):
    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        CALLS.append(str(messages)[:120])
        return "SCRIPTED OUTPUT: the crew completed its task."


def install(placeholder_key="harness-placeholder"):
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", placeholder_key)
    crewai.LLM = lambda **kwargs: ScriptedLLM(model=str(kwargs.get("model", "scripted")))
