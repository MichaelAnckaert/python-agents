Quick Start Guide
=================

Installation
------------

Install python-agents using pip:

.. code-block:: bash

   pip install python-agents

Or using uv:

.. code-block:: bash

   uv add python-agents

Basic Usage
-----------

LLMClient Example
~~~~~~~~~~~~~~~~~

The simplest way to use python-agents is with the ``LLMClient``:

.. code-block:: python

   from python_agents.client import LLMClient
   import asyncio

   async def main():
       client = LLMClient("openai/gpt-4.1-mini")
       response = await client.invoke("What is 1+1?")
       print(response.message.content)

   asyncio.run(main())

Tool Calling
~~~~~~~~~~~~

Define Python functions and register them as tools:

.. code-block:: python

   def calculator(operation: str, a: int, b: int):
       """Perform operation on parameters a and b.

       :param operation: string representing the operation. Supported: '+', '-', '*', '/'.
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

   async def test_tool():
       client = LLMClient("openai/gpt-4.1-mini")
       client.add_tool(calculator)
       response = await client.invoke("What is 7+2 and what is 9*45?")
       print(response.message.content)

ReactAgent Example
~~~~~~~~~~~~~~~~~~

Use ``ReactAgent`` for multi-step reasoning tasks:

.. code-block:: python

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
           "Look up when the iPhone was first released, then find what major world "
           "event happened that same year, then tell me who was the US president during that event.",
           verbose=True
       )
       print(f"Agent final answer: {response}")

   if __name__ == "__main__":
       asyncio.run(run_agent())

Key Concepts
------------

1. **Create tools** as Python functions with type hints and docstrings
2. **Instantiate** an ``LLMClient`` with your model name
3. **Register tools** using ``client.add_tool(func)``
4. **Create an Agent** (``ReactAgent``) with the client
5. **Run the agent** with ``agent.run()`` for multi-step tasks
6. **Use async/await** - all operations are asynchronous

Next Steps
----------

* Explore the :doc:`api` reference for detailed documentation
* Check the GitHub repository for more examples
* Learn about the REACT pattern and how agents reason step-by-step
