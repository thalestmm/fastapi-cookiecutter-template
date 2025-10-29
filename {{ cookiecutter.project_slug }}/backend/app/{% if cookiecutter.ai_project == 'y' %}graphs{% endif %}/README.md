# LangGraph Agent Workflows

This directory contains LangGraph-based agent workflows for AI functionality.

## Overview

The agent system uses:
- **LangChain**: For LLM integration and tool management
- **LangGraph**: For building stateful, multi-step workflows
- **OpenAI**: As the default LLM provider

## Architecture

```
graphs/
├── __init__.py           # Main exports
├── workflow.py           # Workflow definition
├── nodes/                # Graph nodes
│   ├── agent.py         # Agent logic node
│   └── supervisor.py    # Workflow control logic
└── tools/                # LangChain tools
    ├── search.py        # Search tool
    └── calculator.py    # Calculator tool
```

## Workflow

The agent workflow follows this pattern:

```
User Input → Agent Node → Decision
                          ├─→ Use Tools → Tool Node → Back to Agent
                          └─→ Final Response → End
```

1. **Agent Node**: Receives user input, uses LLM to decide on actions
2. **Conditional Edge**: Determines if tools are needed
3. **Tool Node**: Executes requested tools
4. **Loop**: Process continues until agent has final answer

## Usage

### Via API

**Simple Query:**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 25 * 4?"
  }'
```

**Chat with History:**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 100 / 5",
    "conversation_history": []
  }'
```

### In Python Code

```python
from langchain_core.messages import HumanMessage
from app.graphs import agent_workflow

# Create initial state
state = {
    "messages": [HumanMessage(content="What is 10 + 5?")]
}

# Run workflow
result = agent_workflow.invoke(state)

# Get response
response = result["messages"][-1].content
print(response)
```

## Creating Custom Tools

### 1. Define the Tool

Create a new file in `tools/` directory:

```python
# tools/my_tool.py
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def my_custom_tool(input_param: str) -> str:
    """
    Description of what your tool does.
    
    This docstring is important - the LLM uses it to understand
    when and how to use the tool.
    
    Args:
        input_param: Description of the parameter
    
    Returns:
        Result as a string
    """
    logger.info(f"Running my_custom_tool with: {input_param}")
    
    # Your tool logic here
    result = process_input(input_param)
    
    return str(result)
```

### 2. Register the Tool

Add to `tools/__init__.py`:

```python
from app.graphs.tools.my_tool import my_custom_tool

def get_all_tools() -> List[Tool]:
    return [
        search_tool,
        calculator_tool,
        my_custom_tool,  # Add your tool
    ]
```

### 3. Use the Tool

The agent will automatically discover and use your tool when appropriate!

## Creating Custom Nodes

### Define a New Node

```python
# nodes/my_node.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def my_custom_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom node function.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state
    """
    logger.info("My custom node running...")
    
    messages = state.get("messages", [])
    
    # Your node logic here
    # Process messages, call APIs, etc.
    
    return {
        "messages": messages + [new_message],
    }
```

### Add to Workflow

Update `workflow.py`:

```python
from app.graphs.nodes.my_node import my_custom_node

workflow.add_node("my_node", my_custom_node)
workflow.add_edge("agent", "my_node")
workflow.add_edge("my_node", "tools")
```

## Configuration

Set these environment variables:

```bash
# Required
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4  # or gpt-3.5-turbo

# Optional
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Available Tools

### Calculator Tool
Performs mathematical calculations.

```python
# Example usage by agent
"Calculate 25 * 4"
# → 100
```

### Search Tool
Searches for information (placeholder - implement actual search).

```python
# Example usage by agent
"Search for the capital of France"
# → Search results...
```

## Testing the Agent

### Unit Tests

```python
import pytest
from langchain_core.messages import HumanMessage
from app.graphs import agent_workflow

def test_calculator_tool():
    """Test that agent can use calculator."""
    state = {
        "messages": [HumanMessage(content="What is 10 * 5?")]
    }
    
    result = agent_workflow.invoke(state)
    response = result["messages"][-1].content
    
    assert "50" in response
```

### Integration Tests

```python
def test_agent_endpoint(client):
    """Test agent API endpoint."""
    response = client.post(
        "/api/v1/agent/query",
        json={"query": "Calculate 2 + 2"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "4" in data["answer"]
```

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.graphs")
logger.setLevel(logging.DEBUG)
```

### Visualize the Workflow

```python
from app.graphs.workflow import create_agent_workflow

workflow = create_agent_workflow()

# Get mermaid diagram
print(workflow.get_graph().draw_mermaid())
```

### Inspect State at Each Step

```python
# Run with streaming to see each step
for event in agent_workflow.stream(initial_state):
    print(event)
```

## Advanced Features

### Streaming Responses

```python
async def stream_agent_response(query: str):
    """Stream agent responses token by token."""
    state = {"messages": [HumanMessage(content=query)]}
    
    async for event in agent_workflow.astream(state):
        # Process streaming events
        yield event
```

### Persistent State

```python
from langgraph.checkpoint import MemorySaver

# Create workflow with checkpointing
checkpointer = MemorySaver()
workflow = create_agent_workflow().compile(checkpointer=checkpointer)

# Run with thread_id for persistence
config = {"configurable": {"thread_id": "user_123"}}
result = workflow.invoke(state, config)
```

### Human-in-the-Loop

```python
from langgraph.prebuilt import create_agent_executor

# Add human approval node
def human_approval_node(state):
    """Wait for human approval before continuing."""
    # Implement approval logic
    pass

workflow.add_node("human_approval", human_approval_node)
workflow.add_edge("agent", "human_approval")
workflow.add_edge("human_approval", "tools")
```

## Best Practices

1. **Tool Descriptions**: Write clear, detailed docstrings for tools
2. **Error Handling**: Always catch and log exceptions in nodes
3. **State Management**: Keep state minimal and serializable
4. **Testing**: Test nodes independently before integration
5. **Logging**: Log important events for debugging
6. **Timeouts**: Set appropriate timeouts for LLM calls
7. **Cost Management**: Monitor token usage in production

## Troubleshooting

### "No OpenAI API key found"
Set the `OPENAI_API_KEY` environment variable.

### "Tool not being used"
- Check tool docstring is clear and descriptive
- Verify tool is registered in `get_all_tools()`
- Try with a more explicit query

### "Agent loops indefinitely"
- Check `should_continue` logic
- Add max iteration limit
- Review tool return values

### "Import errors"
Ensure all dependencies are installed:
```bash
pip install langchain langgraph langchain-openai
```

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## Examples

Check `tests/test_agent.py` for more usage examples.

