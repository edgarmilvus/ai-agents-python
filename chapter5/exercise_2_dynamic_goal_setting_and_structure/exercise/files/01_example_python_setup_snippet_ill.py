#!/usr/bin/env python3
# -*- coding coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import List

# Define the mandatory structure for the research output
class ResearchReport(BaseModel):
    """
    A structured report containing research findings based on specific temporal constraints.
    """
    query: str = Field(description="The original topic provided for research.")
    cutoff_date_used: str = Field(description="The date used to filter sources (YYYY-MM-DD).")
    summary: str = Field(description="A concise summary of findings, strictly adhering to the cutoff date.")
    source_count: int = Field(description="Total number of unique, relevant sources found and cited.")
    key_insights: List[str] = Field(description="3 to 5 critical takeaways from the research.")

# In a full implementation, this schema would be passed to the agent/task definition
# to instruct the LLM on the required output format.
