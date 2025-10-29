"""
LangChain tools for the agent.

This module contains custom tools that can be used by LangChain agents
in the workflow.
"""
from typing import List
from langchain_core.tools import Tool

from app.graphs.tools.search import search_tool
from app.graphs.tools.calculator import calculator_tool


def get_all_tools() -> List[Tool]:
    """
    Get all available tools for the agent.
    
    Returns:
        List of LangChain Tool instances
    """
    return [
        search_tool,
        calculator_tool,
    ]


__all__ = [
    "get_all_tools",
    "search_tool",
    "calculator_tool",
]

