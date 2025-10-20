# python-agents
Easy to use and powerful AI Agent development framework.

`python-agents` contains a basic REACT agent framework and helper classes to call Large Language Models.

## Agent Example

Here's how to use the core `ReactAgent` class with custom tools:

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
    """Search the internet for the given query."""
    tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = tavily_client.search(query)
    return response

def get_random_number() -> int:
    """Return a random number between 1 and 100."""
    return random.randint(0, 100)

def calculator(operation: str, a: int, b: int):
    """Perform operation on parameters a and b."""
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
    client = LLMClient("openai/gpt-4.1-mini")
    client.add_tool(calculator)
    client.add_tool(get_random_number)
    client.add_tool(search_internet)
    agent = ReactAgent(client)

    response = await agent.run(
        "Look up when the iPhone was first released, then find what major world event happened that same year, then tell me who was the US president during that event.",
        verbose=True
    )
    print(f"Agent final answer: {response}")

if __name__ == "__main__":
    asyncio.run(run_agent())
```

### Steps:
1. **Create tools** as Python functions. Tools can be any function your agent might need (e.g., internet search, calculator).
2. **Instantiate** an `LLMClient`, providing your model name or endpoint.
3. **Register your tools** with `client.add_tool`.
4. **Create the Agent** (here, `ReactAgent`) with the client.
5. **Invoke `agent.run()`** with your prompt/query and optional arguments like `verbose=True`.
6. **Run everything inside an event loop** (as `agent.run` is async).

The agent will automatically determine which tools to use and in what sequence to fulfill the given instruction.

## LLMClient example
```python
client = LLMClient("openai/gpt-4.1-mini")
response = await client.invoke("What is 1+1?")
print(response.message.content)
```


## Tool Calling
`python-agents` supports tool calling:

```python
# Define a python function to be used as a tool
def calculator(operation: str, a: int, b: int):
    """Performation operation on parameters a and b.

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


async def test_simple_tool():
    client = LLMClient("openai/gpt-4.1-mini")
    client.add_tool(calculator)
    response = await client.invoke("What is 7+2 and what is 9*45? Use your calculator tool.")
    print(response.message.content)
```
