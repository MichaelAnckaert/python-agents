Using MCP Servers
=================

This guide explains how to integrate Model Context Protocol (MCP) servers with python-agents to extend your agent's capabilities with external tools and data sources.

What is MCP?
------------

The Model Context Protocol (MCP) is a standardized protocol that allows AI applications to connect to external data sources and tools. MCP servers expose tools, resources, and prompts that your agents can use to interact with various systems, databases, APIs, and services.

By integrating MCP servers with python-agents, you can:

- **Access external data** through MCP resources
- **Use specialized tools** provided by MCP servers
- **Connect to multiple services** simultaneously
- **Extend agent capabilities** without writing custom tool functions
- **Leverage community MCP servers** for common integrations

Understanding MCPClient
-----------------------

The ``MCPClient`` class provides the interface for connecting to MCP servers and making their tools available to your agents.

Key Features
~~~~~~~~~~~~

- **Async-first design**: Built on asyncio for efficient concurrent operations
- **Automatic tool discovery**: Lists and registers available tools from the MCP server
- **Seamless integration**: Works alongside regular Python function tools
- **Resource management**: Handles connection lifecycle and cleanup

MCPClient Methods
~~~~~~~~~~~~~~~~~

.. py:class:: MCPClient

   Client for connecting to and interacting with MCP servers.

   .. py:method:: __init__()

      Initialize a new MCP client instance.

   .. py:method:: async connect_to_server(command: str, arguments: list[str])

      Connect to an MCP server using stdio transport.

      :param command: The command to execute (e.g., "uv", "python", "node")
      :param arguments: List of arguments to pass to the command
      :type command: str
      :type arguments: list[str]

      The server is started as a subprocess, and communication happens via stdin/stdout.

   .. py:method:: async list_available_tools()

      List all tools available from the connected MCP server.

      :returns: List of tool schemas in OpenAI function format
      :rtype: list[dict]

   .. py:method:: async call_tool(tool_name: str, tool_args: dict[str, Any])

      Call a tool on the MCP server.

      :param tool_name: Name of the tool to call
      :param tool_args: Dictionary of arguments to pass to the tool
      :type tool_name: str
      :type tool_args: dict[str, Any]
      :returns: Tool execution result
      :rtype: Any

   .. py:method:: async cleanup()

      Clean up resources and close the connection to the MCP server.

      Always call this method when you're done using the MCP client,
      preferably in a try/finally block.

Basic Usage
-----------

Simple MCP Integration
~~~~~~~~~~~~~~~~~~~~~~~

Here's a minimal example of connecting to an MCP server:

.. code-block:: python

   import asyncio
   from python_agents.client import MCPClient, LLMClient

   async def main():
       # Create and connect MCP client
       mcp_client = MCPClient()
       await mcp_client.connect_to_server(
           "uv",
           ["run", "/path/to/mcp-server/main.py", "--transport", "stdio"]
       )

       # Create LLM client and register MCP server
       client = LLMClient("openai/gpt-4-turbo")
       client.add_mcp_server(mcp_client)

       # Use the client - MCP tools are now available
       try:
           response = await client.invoke("Use the MCP tools to get information")
           print(response.message.content)
       finally:
           await mcp_client.cleanup()

   asyncio.run(main())

Using Cleanup with LLMClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``LLMClient`` has a built-in cleanup method that handles all registered MCP servers:

.. code-block:: python

   async def main():
       client = LLMClient("openai/gpt-4-turbo")

       # Connect to MCP server
       mcp_client = MCPClient()
       await mcp_client.connect_to_server(
           "python",
           ["/path/to/mcp-server.py"]
       )
       client.add_mcp_server(mcp_client)

       try:
           response = await client.invoke("Your query here")
           print(response.message.content)
       finally:
           # This automatically cleans up all MCP servers
           await client.cleanup()

   asyncio.run(main())

Connecting to Different MCP Servers
------------------------------------

Python MCP Servers
~~~~~~~~~~~~~~~~~~

For MCP servers written in Python:

.. code-block:: python

   mcp_client = MCPClient()
   await mcp_client.connect_to_server(
       "python",
       ["/path/to/server.py", "--transport", "stdio"]
   )

Using uv to Run Python Servers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your MCP server uses uv for dependency management:

.. code-block:: python

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

Node.js MCP Servers
~~~~~~~~~~~~~~~~~~~

For MCP servers written in JavaScript/TypeScript:

.. code-block:: python

   mcp_client = MCPClient()
   await mcp_client.connect_to_server(
       "node",
       ["/path/to/server.js"]
   )

Complete Example: Agent with MCP Server
----------------------------------------

This example demonstrates using an MCP server with a ReactAgent for multi-step tasks:

.. code-block:: python

   import os
   import asyncio
   import random

   from python_agents.client import MCPClient, LLMClient
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


   async def run_agent_with_mcp():
       # Initialize LLM client
       client = LLMClient("anthropic/claude-sonnet-4.5")

       # Add regular Python function tools
       client.add_tool(calculator)
       client.add_tool(get_random_number)
       client.add_tool(search_internet)

       # Connect to MCP server
       mcp_client = MCPClient()
       await mcp_client.connect_to_server(
           "uv",
           [
               "run",
               "/home/michael/projects/iam-mcp-server/main.py",
               "--transport",
               "stdio"
           ]
       )

       # Register MCP server with the client
       client.add_mcp_server(mcp_client)

       # Create ReactAgent
       agent = ReactAgent(client)

       try:
           # Run a complex task that uses both regular tools and MCP tools
           response = await agent.run(
               "Get property information for ID 231852. If there are any rental "
               "candidates, check their financial information to see if they qualify.",
               verbose=True
           )
           print(f"\nAgent final answer: {response}")
       finally:
           # Clean up all resources
           await client.cleanup()


   if __name__ == "__main__":
       asyncio.run(run_agent_with_mcp())

.. note::
   In this example, the agent has access to both:

   - Regular Python tools (calculator, get_random_number, search_internet)
   - MCP server tools (property management tools from the IAM server)

   The LLM can use any available tool to complete the task.

Working with Multiple MCP Servers
----------------------------------

You can connect to multiple MCP servers simultaneously:

.. code-block:: python

   async def multi_server_example():
       client = LLMClient("openai/gpt-4-turbo")

       # Connect to first MCP server (e.g., database access)
       db_mcp = MCPClient()
       await db_mcp.connect_to_server(
           "python",
           ["/path/to/database-mcp-server.py"]
       )
       client.add_mcp_server(db_mcp)

       # Connect to second MCP server (e.g., file system access)
       fs_mcp = MCPClient()
       await fs_mcp.connect_to_server(
           "python",
           ["/path/to/filesystem-mcp-server.py"]
       )
       client.add_mcp_server(fs_mcp)

       # Connect to third MCP server (e.g., API integration)
       api_mcp = MCPClient()
       await api_mcp.connect_to_server(
           "node",
           ["/path/to/api-mcp-server.js"]
       )
       client.add_mcp_server(api_mcp)

       try:
           # Agent now has access to tools from all three MCP servers
           agent = ReactAgent(client)
           response = await agent.run(
               "Query the database, process the files, and sync with the API",
               verbose=True
           )
           print(response)
       finally:
           # Cleanup handles all MCP servers automatically
           await client.cleanup()

   asyncio.run(multi_server_example())

Listing Available Tools
-----------------------

You can inspect what tools an MCP server provides:

.. code-block:: python

   async def list_tools_example():
       mcp_client = MCPClient()
       await mcp_client.connect_to_server(
           "python",
           ["/path/to/server.py"]
       )

       # Get list of available tools
       tools = await mcp_client.list_available_tools()

       print("Available MCP tools:")
       for tool in tools:
           print(f"  - {tool['function']['name']}: {tool['function']['description']}")

       await mcp_client.cleanup()

   asyncio.run(list_tools_example())

Best Practices
--------------

Always Use Cleanup
~~~~~~~~~~~~~~~~~~

**ALWAYS** clean up MCP clients when done to prevent resource leaks:

.. code-block:: python

   # Option 1: Use try/finally
   try:
       response = await client.invoke("query")
   finally:
       await client.cleanup()

   # Option 2: If using LLMClient, cleanup handles all MCP servers
   try:
       response = await agent.run("task")
   finally:
       await client.cleanup()  # Cleans up all registered MCP servers

Error Handling
~~~~~~~~~~~~~~

Handle connection errors gracefully:

.. code-block:: python

   async def safe_mcp_connection():
       mcp_client = MCPClient()

       try:
           await mcp_client.connect_to_server(
               "python",
               ["/path/to/server.py"]
           )

           client = LLMClient("openai/gpt-4-turbo")
           client.add_mcp_server(mcp_client)

           # Use the client
           response = await client.invoke("query")
           return response

       except FileNotFoundError:
           print("Error: MCP server script not found")
       except Exception as e:
           print(f"Error connecting to MCP server: {e}")
       finally:
           await mcp_client.cleanup()

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Use environment variables for server paths:

.. code-block:: python

   import os
   from dotenv import load_dotenv

   load_dotenv()

   async def main():
       mcp_client = MCPClient()
       server_path = os.environ.get("MCP_SERVER_PATH")

       if not server_path:
           raise ValueError("MCP_SERVER_PATH environment variable not set")

       await mcp_client.connect_to_server(
           "python",
           [server_path, "--transport", "stdio"]
       )

       # Continue with setup...

Combining Tools and MCP Servers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Design your application to leverage both regular Python tools and MCP servers:

- **Use Python tools for**: Simple logic, calculations, text processing
- **Use MCP servers for**: External integrations, database access, complex APIs
- **Combine both**: Let the LLM choose the right tool for each subtask

.. code-block:: python

   # Simple local tools
   client.add_tool(calculator)
   client.add_tool(format_text)

   # Complex external integrations via MCP
   client.add_mcp_server(database_mcp)
   client.add_mcp_server(api_mcp)

   # LLM chooses the appropriate tool for each step

Troubleshooting
---------------

MCP Server Won't Start
~~~~~~~~~~~~~~~~~~~~~~

If the MCP server fails to start:

1. **Check the command path**: Ensure the command ("python", "node", "uv") is in your PATH
2. **Verify script path**: Make sure the server script path is absolute and correct
3. **Check permissions**: Ensure the script is executable
4. **Review server logs**: Check if the MCP server is logging errors

.. code-block:: python

   # Use absolute paths
   await mcp_client.connect_to_server(
       "python",
       ["/absolute/path/to/server.py"]
   )

Connection Timeout
~~~~~~~~~~~~~~~~~~

If the connection times out:

- Ensure the MCP server implements the stdio transport protocol correctly
- Check that the server responds to initialization messages
- Verify there are no startup errors in the server

Tools Not Appearing
~~~~~~~~~~~~~~~~~~~

If MCP tools aren't available to the LLM:

1. **Verify registration**: Ensure you called ``client.add_mcp_server(mcp_client)``
2. **Check tool listing**: Use ``await mcp_client.list_available_tools()`` to verify
3. **Test server independently**: Run the MCP server directly to ensure it works

.. code-block:: python

   # Debug: List tools before using
   tools = await mcp_client.list_available_tools()
   print(f"Found {len(tools)} tools from MCP server")
   for tool in tools:
       print(f"  - {tool['function']['name']}")

Common Patterns
---------------

Lazy MCP Connection
~~~~~~~~~~~~~~~~~~~

Connect to MCP server only when needed:

.. code-block:: python

   class LazyMCPClient:
       def __init__(self, command, args):
           self.command = command
           self.args = args
           self.mcp_client = None

       async def get_client(self):
           if self.mcp_client is None:
               self.mcp_client = MCPClient()
               await self.mcp_client.connect_to_server(
                   self.command,
                   self.args
               )
           return self.mcp_client

       async def cleanup(self):
           if self.mcp_client is not None:
               await self.mcp_client.cleanup()

Reusable MCP Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a configuration system for MCP servers:

.. code-block:: python

   from dataclasses import dataclass

   @dataclass
   class MCPServerConfig:
       name: str
       command: str
       args: list[str]


   async def setup_mcp_servers(client: LLMClient, configs: list[MCPServerConfig]):
       """Set up multiple MCP servers from configuration."""
       mcp_clients = []

       for config in configs:
           mcp_client = MCPClient()
           await mcp_client.connect_to_server(config.command, config.args)
           client.add_mcp_server(mcp_client)
           mcp_clients.append(mcp_client)
           print(f"Connected to MCP server: {config.name}")

       return mcp_clients


   # Usage
   async def main():
       client = LLMClient("openai/gpt-4-turbo")

       server_configs = [
           MCPServerConfig(
               name="Database",
               command="python",
               args=["/path/to/db-server.py"]
           ),
           MCPServerConfig(
               name="API",
               command="node",
               args=["/path/to/api-server.js"]
           ),
       ]

       mcp_clients = await setup_mcp_servers(client, server_configs)

       try:
           # Use the client
           response = await client.invoke("query")
       finally:
           await client.cleanup()

Next Steps
----------

* Learn about :doc:`tool_calling` to create custom Python tools
* Explore :doc:`configure_providers` to set up different LLM providers
* Check the :doc:`../api` reference for detailed API documentation
* Browse the MCP specification at https://modelcontextprotocol.io
* Find community MCP servers at https://github.com/modelcontextprotocol/servers

Additional Resources
--------------------

* **MCP Protocol Specification**: https://modelcontextprotocol.io/docs
* **Official MCP Servers**: https://github.com/modelcontextprotocol/servers
* **Building MCP Servers**: See the MCP documentation for server development guides
* **python-agents GitHub**: https://github.com/yourusername/python-agents (for issues and examples)
