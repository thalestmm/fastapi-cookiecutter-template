"""
Agent node for processing user requests.
"""
import logging
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from app.core.config import settings
from app.graphs.tools import get_all_tools

logger = logging.getLogger(__name__)


def get_llm():
    """
    Get the configured LLM instance.
    
    Returns:
        ChatOpenAI instance
    """
    return ChatOpenAI(
        model=settings.LLM_MODEL or "gpt-4",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.7,
    )


def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent node that processes the current state and decides what to do next.
    
    This node uses an LLM to analyze the user's request and decide whether
    to use tools or provide a direct response.
    
    Args:
        state: Current workflow state containing messages and other data
    
    Returns:
        Updated state with agent's response
    """
    logger.info("Agent node processing...")
    
    messages = state.get("messages", [])
    
    # Get LLM and tools
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # Add system message if not present
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_message = SystemMessage(
            content="You are a helpful AI assistant. You have access to tools to help answer questions. "
                   "Use tools when you need additional information or capabilities."
        )
        messages = [system_message] + messages
    
    # Get response from LLM
    response = llm_with_tools.invoke(messages)
    
    logger.info(f"Agent response: {response.content[:100]}...")
    
    # Update state with agent's response
    return {
        "messages": messages + [response],
    }


# Create tool node for executing tools
tool_node = ToolNode(get_all_tools())


__all__ = ["agent_node", "tool_node"]

