"""
LangGraph workflow definition.

This module defines the agent workflow using LangGraph's StateGraph.
"""
import logging
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.graphs.nodes import agent_node, tool_node, should_continue

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """
    State schema for the agent workflow.
    
    Attributes:
        messages: List of messages in the conversation
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_agent_workflow() -> StateGraph:
    """
    Create and configure the agent workflow graph.
    
    The workflow consists of:
    1. Agent node - processes user input and decides on actions
    2. Tool node - executes tools if requested by the agent
    3. Conditional edge - determines whether to continue or end
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Creating agent workflow...")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edge from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    logger.info("Workflow created successfully")
    
    # Compile the graph
    return workflow.compile()


# Create a singleton instance of the workflow
graph: StateGraph = create_agent_workflow()


__all__ = ["graph", "create_agent_workflow", "AgentState"]

