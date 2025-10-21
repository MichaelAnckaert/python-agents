# python-agents

[![PyPI version](https://badge.fury.io/py/python-agents.svg)](https://badge.fury.io/py/python-agents)
[![Documentation](https://readthedocs.org/projects/python-agents/badge/?version=latest)](https://python-agents.readthedocs.io/en/latest/)

python-agents is an easy to use and powerful AI Agent development framework that implements the REACT (Reasoning and Acting) pattern for building agents with tool-calling capabilities.

The library provides a minimal but powerful abstraction for creating agents that can reason step-by-step and use tools to accomplish complex tasks.

## Features

- **REACT Agent Pattern**: Step-by-step reasoning with tool calling
- **Simple Tool Integration**: Convert Python functions to agent tools automatically
- **MCP Server Support**: Connect to Model Context Protocol servers for external integrations
- **Async-First Design**: Built on async/await for efficient concurrent operations
- **OpenRouter Compatible**: Works with any OpenAI-compatible API endpoint

## Installation

Install using pip:

```bash
pip install python-agents
```

Or using uv:

```bash
uv add python-agents
```

## Quick Start

### Basic LLMClient Usage

```python
from python_agents.client import LLMClient
import asyncio

async def main():
    client = LLMClient("openai/gpt-4.1-mini")
    response = await client.invoke("What is 1+1?")
    print(response.message.content)

asyncio.run(main())
```

### ReactAgent with Tool Calling

The ReactAgent enables multi-step reasoning with automatic tool selection and execution:

```python
import os
import asyncio
import random

from python_agents.client import LLMClient
from python_agents.agents import ReactAgent
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def search_internet(query: str):
    """Search the internet for the given query.

    :param query: Query to search the internet for.
    :return: Response to your query
    """
    tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = tavily_client.search(query)
    return response


def get_random_number() -> int:
    """Return a random number between 1 and 100.

    :return: random number (integer)
    """
    return random.randint(0, 100)


def calculator(operation: str, a: int, b: int):
    """Perform operation on parameters a and b.

    :param operation: string representing the operation. Supported operations: '+', '-', '*', '/'.
    :param a: First operand.
    :param b: Second operand.
    :return: result of the operation.
    """
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        return a / b
    else:
        return "Wrong operation!"


async def run_agent():
    # Create LLM client
    client = LLMClient("openai/gpt-4.1-mini")

    # Register tools - Python functions the agent can call
    client.add_tool(calculator)
    client.add_tool(get_random_number)
    client.add_tool(search_internet)

    # Create ReactAgent for multi-step reasoning
    agent = ReactAgent(client)

    # Run a complex task requiring multiple steps
    response = await agent.run(
        "Look up when the iPhone was first released, then find what major world "
        "event happened that same year, then tell me who was the US president during that event.",
        verbose=True
    )
    print(f"Agent final answer: {response}")


if __name__ == "__main__":
    asyncio.run(run_agent())
```

### How ReactAgent Works

1. **Receives a task**: You provide a natural language task description
2. **Reasons about the task**: The agent breaks it down into steps
3. **Selects tools**: Chooses appropriate tools for each step
4. **Executes tools**: Calls tools with the right arguments
5. **Iterates**: Continues reasoning and acting until the task is complete
6. **Returns result**: Provides the final answer

## Using MCP Servers

Extend your agent's capabilities by connecting to Model Context Protocol (MCP) servers:

```python
import asyncio
from python_agents.client import MCPClient, LLMClient
from python_agents.agents import ReactAgent


async def run_agent_with_mcp():
    # Initialize LLM client
    client = LLMClient("anthropic/claude-sonnet-4.5")

    # Add regular Python function tools
    client.add_tool(calculator)
    client.add_tool(search_internet)

    # Connect to an MCP server
    mcp_client = MCPClient()
    await mcp_client.connect_to_server(
        "uv",
        [
            "run",
            "/path/to/mcp-server/main.py",
            "--transport",
            "stdio"
        ]
    )

    # Register MCP server with the client
    client.add_mcp_server(mcp_client)

    # Create ReactAgent
    agent = ReactAgent(client)

    try:
        # Agent now has access to both Python tools and MCP server tools
        response = await agent.run(
            "Your complex task using both local and MCP tools",
            verbose=True
        )
        print(f"Agent final answer: {response}")
    finally:
        # Always clean up resources
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(run_agent_with_mcp())
```

## Environment Setup

Create a `.env` file:

```bash
# For OpenRouter (default)
OPENAI_API_KEY=your-openrouter-api-key
# For Tavily internet search (optional)
TAVILY_API_KEY=your-tavily-api-key
```

## Supported Models

Works with any OpenAI-compatible API:

```python
# Via OpenRouter (default)
client = LLMClient("openai/gpt-4-turbo")
client = LLMClient("anthropic/claude-sonnet-4.5")
client = LLMClient("google/gemini-pro")

# Direct OpenAI
client = LLMClient("gpt-4-turbo", base_url="https://api.openai.com/v1")

# Local models (e.g., Ollama)
client = LLMClient("llama3", base_url="http://localhost:11434/v1")
```

## Documentation

Full documentation is available at [python-agents.readthedocs.io](https://python-agents.readthedocs.io/en/latest/)

### Key Topics

- **[Quick Start Guide](https://python-agents.readthedocs.io/en/latest/quickstart.html)** - Get started quickly
- **[Tool Calling](https://python-agents.readthedocs.io/en/latest/howto/tool_calling.html)** - Create and use custom tools
- **[Using MCP Servers](https://python-agents.readthedocs.io/en/latest/howto/using_mcp_servers.html)** - Integrate external services
- **[Configure Providers](https://python-agents.readthedocs.io/en/latest/howto/configure_providers.html)** - Set up different LLM providers
- **[API Reference](https://python-agents.readthedocs.io/en/latest/api.html)** - Complete API documentation

## Key Concepts

### Tools

Tools are Python functions that your agent can call. Simply decorate them with type hints and docstrings:

```python
def get_weather(location: str, units: str = "celsius") -> str:
    """Get the weather for a location.

    :param location: City name or "City, Country" format
    :param units: Temperature units - "celsius" or "fahrenheit"
    :return: Weather information
    """
    # Your implementation
    return f"Weather in {location}: 22°{units[0].upper()}"

client.add_tool(get_weather)
```

### ReactAgent vs LLMClient

- **LLMClient**: Single-turn interactions, handles one round of tool calling
- **ReactAgent**: Multi-turn reasoning, iterates until task completion, implements REACT pattern

### MCP Integration

MCP (Model Context Protocol) servers provide:
- External data sources
- Specialized tools
- Third-party integrations
- Community-built capabilities

Combine Python tools with MCP servers for maximum flexibility.

## Best Practices

1. **Write clear docstrings**: Agents rely on docstrings to understand tool capabilities
2. **Use type hints**: Required for automatic schema generation
3. **Handle errors gracefully**: Return error messages as strings
4. **Set max iterations**: Prevent infinite loops with `ReactAgent(client, max_iterations=10)`
5. **Use verbose mode**: Enable `verbose=True` during development
6. **Clean up resources**: Always call `await client.cleanup()` when using MCP servers

## Examples

Check the `/examples` directory for more:

- Basic LLMClient usage
- ReactAgent with multiple tools
- MCP server integration
- Multi-step reasoning tasks

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.

## Links

- **Documentation**: https://python-agents.readthedocs.io/
- **MCP Specification**: https://modelcontextprotocol.io/
- **OpenRouter**: https://openrouter.ai/

## Support

For questions and support:
- Open an issue on GitHub
- Check the documentation
- Join our community discussions
