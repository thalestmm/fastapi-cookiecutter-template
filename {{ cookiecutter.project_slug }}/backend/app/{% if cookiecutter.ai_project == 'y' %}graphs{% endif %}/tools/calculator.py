"""
Calculator tool for the agent.
"""
import logging
from typing import Union
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def calculator_tool(expression: str) -> str:
    """
    Calculate mathematical expressions.
    
    Use this tool when you need to perform mathematical calculations.
    Supports basic arithmetic operations.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
    
    Returns:
        The result of the calculation as a string
    """
    logger.info(f"Calculating: {expression}")
    
    try:
        # Safety: Only allow basic mathematical operations
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and basic operators (+, -, *, /, parentheses) are allowed."
        
        # Evaluate the expression
        result = eval(expression)
        logger.info(f"Result: {result}")
        
        return str(result)
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return f"Error calculating expression: {str(e)}"


__all__ = ["calculator_tool"]

