"""
Supervisor node for controlling workflow execution.
"""
import logging
from typing import Dict, Any, Literal
from langchain_core.messages import AIMessage, ToolMessage

logger = logging.getLogger(__name__)


def should_continue(state: Dict[str, Any]) -> Literal["continue", "end"]:
    """
    Determine whether the workflow should continue or end.
    
    This function checks if the last message from the agent contains
    tool calls. If it does, the workflow continues to execute the tools.
    Otherwise, it ends.
    
    Args:
        state: Current workflow state
    
    Returns:
        "continue" if tools need to be executed, "end" otherwise
    """
    messages = state.get("messages", [])
    
    if not messages:
        logger.info("No messages, ending workflow")
        return "end"
    
    last_message = messages[-1]
    
    # Check if last message has tool calls
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
        tool_calls = last_message.tool_calls
        if tool_calls:
            logger.info(f"Tool calls found: {len(tool_calls)}, continuing workflow")
            return "continue"
    
    logger.info("No tool calls, ending workflow")
    return "end"


__all__ = ["should_continue"]

