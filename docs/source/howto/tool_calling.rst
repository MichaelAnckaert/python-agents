Tool Calling with Python Functions
===================================

This guide covers everything you need to know about creating and using tools in python-agents. Tools are Python functions that your AI agent can call to perform actions, retrieve information, or process data.

Understanding Tool Calling
--------------------------

When you register a Python function as a tool, python-agents automatically:

1. **Generates a schema** from your function signature, type hints, and docstring
2. **Sends the schema** to the LLM so it knows what tools are available
3. **Executes the function** when the LLM requests to use it
4. **Returns the result** back to the LLM to inform its next steps

The quality of your tool's docstring and type hints directly impacts how well the LLM understands and uses your tools.

Basic Tool Creation
-------------------

Simple Tool Example
~~~~~~~~~~~~~~~~~~~

Here's a minimal tool that the LLM can call:

.. code-block:: python

   from python_agents.client import LLMClient
   import asyncio

   def get_current_time() -> str:
       """Get the current time.

       Returns:
           The current time as a string
       """
       from datetime import datetime
       return datetime.now().strftime("%H:%M:%S")

   async def main():
       client = LLMClient("openai/gpt-4-turbo")
       client.add_tool(get_current_time)

       response = await client.invoke("What time is it?")
       print(response.message.content)

   asyncio.run(main())

Key Requirements
~~~~~~~~~~~~~~~~

Every tool function must have:

1. **Type hints** for all parameters
2. **Return type annotation**
3. **Docstring** explaining what the function does
4. **Parameter descriptions** in the docstring

Type Hints and Annotations
---------------------------

Supported Parameter Types
~~~~~~~~~~~~~~~~~~~~~~~~~

python-agents supports JSON-serializable types for tool parameters:

.. code-block:: python

   def example_tool(
       text: str,           # String parameter
       count: int,          # Integer parameter
       price: float,        # Float parameter
       enabled: bool,       # Boolean parameter
       tags: list[str],     # List of strings
       metadata: dict,      # Dictionary
   ) -> str:
       """Example showing all supported parameter types."""
       return "Success"

.. warning::
   Complex objects, custom classes, and non-JSON-serializable types are **not supported** as parameters. The LLM can only pass basic JSON types.

Optional Parameters
~~~~~~~~~~~~~~~~~~~

Use default values to make parameters optional:

.. code-block:: python

   def search_products(
       query: str,
       category: str = "all",
       max_results: int = 10,
       include_sold_out: bool = False
   ) -> str:
       """Search for products in the catalog.

       Args:
           query: Search query string
           category: Product category to search in. Defaults to "all"
           max_results: Maximum number of results to return. Defaults to 10
           include_sold_out: Whether to include out-of-stock items. Defaults to False

       Returns:
           JSON string containing search results
       """
       # Implementation here
       results = []
       return str(results)

The LLM can call this tool with just the required ``query`` parameter, or include optional parameters as needed.

Return Types
~~~~~~~~~~~~

Tools should return JSON-serializable types. The result is automatically stringified before being sent back to the LLM:

.. code-block:: python

   def calculate(a: int, b: int) -> int:
       """Add two numbers."""
       return a + b  # Returns integer, stringified to "42"

   def get_user_info(user_id: str) -> dict:
       """Get user information."""
       return {"id": user_id, "name": "Alice"}  # Returns dict, stringified

   def list_files(directory: str) -> list[str]:
       """List files in directory."""
       return ["file1.txt", "file2.py"]  # Returns list, stringified

Documenting Tools
-----------------

The Importance of Good Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LLM relies entirely on your docstring to understand:

- **What** the tool does
- **When** to use it
- **What parameters** it needs
- **What it returns**

A well-documented tool is used correctly. A poorly documented tool is used incorrectly or not at all.

Docstring Format
~~~~~~~~~~~~~~~~

Use Google-style or reStructuredText docstrings with clear sections:

.. code-block:: python

   def send_email(
       recipient: str,
       subject: str,
       body: str,
       cc: list[str] = None,
       priority: str = "normal"
   ) -> bool:
       """Send an email message.

       This function sends an email to the specified recipient with the given
       subject and body. It supports CC recipients and priority levels.

       Args:
           recipient: Email address of the primary recipient
           subject: Email subject line
           body: Email body content (plain text)
           cc: List of CC email addresses. Optional.
           priority: Priority level - "low", "normal", or "high". Defaults to "normal"

       Returns:
           True if email was sent successfully, False otherwise

       Note:
           The email is sent asynchronously. This function returns immediately
           after queuing the email for delivery.
       """
       # Implementation
       return True

Best Practices for Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**DO:**

- Be specific and descriptive
- Explain the purpose clearly
- Document all parameters with their expected format
- Mention valid values for string parameters
- Include examples when behavior might be unclear
- Note any side effects or important limitations

**DON'T:**

- Be vague ("does stuff", "processes data")
- Skip parameter descriptions
- Assume the LLM knows your domain-specific terms
- Forget to document default values

Example Comparison
~~~~~~~~~~~~~~~~~~

**Bad docstring:**

.. code-block:: python

   def process_order(order_id: str, action: str) -> str:
       """Process an order."""
       pass

Problems: What does "process" mean? What actions are valid? What does it return?

**Good docstring:**

.. code-block:: python

   def process_order(order_id: str, action: str) -> str:
       """Perform an action on an existing order.

       This function allows you to modify or query existing orders in the system.

       Args:
           order_id: The unique order identifier (format: ORD-XXXXX)
           action: Action to perform. Valid values:
               - "cancel": Cancel the order
               - "ship": Mark order as shipped
               - "refund": Process a refund
               - "status": Get current order status

       Returns:
           Success message for cancel/ship/refund actions, or order status
           information for status action. Returns error message if order_id
           is invalid or action fails.
       """
       pass

Advanced Tool Patterns
----------------------

Tools That Return Structured Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When returning complex data, use JSON format and document the structure:

.. code-block:: python

   import json

   def get_weather(location: str, units: str = "celsius") -> str:
       """Get current weather information for a location.

       Args:
           location: City name or "City, Country" format
           units: Temperature units - "celsius" or "fahrenheit". Defaults to "celsius"

       Returns:
           JSON string with weather data containing:
           - temperature (float): Current temperature in specified units
           - conditions (str): Weather conditions (e.g., "sunny", "rainy")
           - humidity (int): Humidity percentage (0-100)
           - wind_speed (float): Wind speed in km/h or mph

       Example return value:
           {"temperature": 22.5, "conditions": "partly cloudy",
            "humidity": 65, "wind_speed": 12.3}
       """
       weather_data = {
           "temperature": 22.5,
           "conditions": "partly cloudy",
           "humidity": 65,
           "wind_speed": 12.3
       }
       return json.dumps(weather_data)

Tools with External Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tools can use external libraries and APIs:

.. code-block:: python

   import os
   import requests

   def search_wikipedia(query: str, max_results: int = 3) -> str:
       """Search Wikipedia and return article summaries.

       Uses the Wikipedia API to search for articles matching the query
       and returns brief summaries of the top results.

       Args:
           query: Search terms to look up on Wikipedia
           max_results: Maximum number of results to return (1-10). Defaults to 3

       Returns:
           Formatted string with article titles and summaries, separated by newlines.
           Returns "No results found" if query doesn't match any articles.
       """
       url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
       results = []

       # Implementation using requests library
       response = requests.get(f"{url}{query}")
       if response.status_code == 200:
           data = response.json()
           results.append(f"{data['title']}: {data['extract']}")

       return "\n\n".join(results) if results else "No results found"

Error Handling in Tools
~~~~~~~~~~~~~~~~~~~~~~~~

Tools should handle errors gracefully and return informative messages:

.. code-block:: python

   def divide_numbers(a: float, b: float) -> str:
       """Divide two numbers.

       Args:
           a: The dividend (number to be divided)
           b: The divisor (number to divide by)

       Returns:
           The result of a divided by b, or an error message if division
           is not possible (e.g., division by zero).
       """
       try:
           if b == 0:
               return "Error: Cannot divide by zero"
           result = a / b
           return f"Result: {result}"
       except Exception as e:
           return f"Error performing division: {str(e)}"

.. note::
   Return error messages as strings rather than raising exceptions. This allows
   the LLM to see what went wrong and potentially retry or take a different approach.

Tools with Side Effects
~~~~~~~~~~~~~~~~~~~~~~~

Document side effects clearly so the LLM understands the impact:

.. code-block:: python

   def create_database_user(
       username: str,
       email: str,
       role: str = "user"
   ) -> str:
       """Create a new user account in the database.

       **WARNING**: This function has side effects - it modifies the database.

       Args:
           username: Unique username (3-20 characters, alphanumeric and underscore only)
           email: User's email address (must be valid email format)
           role: User role - "user", "admin", or "moderator". Defaults to "user"

       Returns:
           Success message with user ID if created, or error message if username/email
           already exists or validation fails.

       Side Effects:
           - Creates a new row in the users table
           - Sends a welcome email to the provided email address
           - Logs the creation event in the audit log
       """
       # Implementation
       return f"User {username} created with ID: 12345"

Complete Example: Building a File System Agent
-----------------------------------------------

Here's a complete example showing multiple tools working together:

.. code-block:: python

   import os
   from pathlib import Path
   from python_agents.client import LLMClient
   from python_agents.agents import ReactAgent
   import asyncio

   def list_directory(path: str = ".") -> str:
       """List files and directories in the specified path.

       Args:
           path: Directory path to list. Defaults to current directory (".")

       Returns:
           Formatted list of files and directories with type indicators.
           Directories are marked with [DIR], files show their size in bytes.
           Returns error message if path doesn't exist or isn't accessible.
       """
       try:
           items = []
           for item in Path(path).iterdir():
               if item.is_dir():
                   items.append(f"[DIR] {item.name}")
               else:
                   size = item.stat().st_size
                   items.append(f"[FILE] {item.name} ({size} bytes)")
           return "\n".join(items) if items else "Directory is empty"
       except Exception as e:
           return f"Error: {str(e)}"

   def read_file(filepath: str, max_lines: int = 100) -> str:
       """Read and return the contents of a text file.

       Args:
           filepath: Path to the file to read
           max_lines: Maximum number of lines to read. Defaults to 100.
                     Use this to avoid reading huge files entirely.

       Returns:
           File contents as a string, limited to max_lines.
           Returns error message if file doesn't exist, isn't readable,
           or isn't a text file.
       """
       try:
           with open(filepath, 'r') as f:
               lines = [f.readline() for _ in range(max_lines)]
               content = ''.join(lines)
               return content if content else "File is empty"
       except UnicodeDecodeError:
           return "Error: File is not a text file"
       except Exception as e:
           return f"Error reading file: {str(e)}"

   def search_files(directory: str, pattern: str) -> str:
       """Search for files matching a pattern in a directory.

       Args:
           directory: Directory path to search in
           pattern: Filename pattern to match (e.g., "*.txt", "test_*.py")
                   Supports wildcards: * (any characters) and ? (single character)

       Returns:
           List of matching file paths, one per line.
           Returns "No files found" if no matches.
           Returns error message if directory is invalid.
       """
       try:
           matches = list(Path(directory).glob(pattern))
           if matches:
               return "\n".join(str(m) for m in matches)
           return "No files found matching pattern"
       except Exception as e:
           return f"Error searching files: {str(e)}"

   def get_file_info(filepath: str) -> str:
       """Get detailed information about a file.

       Args:
           filepath: Path to the file

       Returns:
           JSON string containing file metadata:
           - size: File size in bytes
           - created: Creation timestamp
           - modified: Last modification timestamp
           - is_directory: Boolean indicating if path is a directory
           - extension: File extension (empty string for directories)
       """
       try:
           path = Path(filepath)
           stat = path.stat()
           info = {
               "size": stat.st_size,
               "created": stat.st_ctime,
               "modified": stat.st_mtime,
               "is_directory": path.is_dir(),
               "extension": path.suffix
           }
           import json
           return json.dumps(info, indent=2)
       except Exception as e:
           return f"Error getting file info: {str(e)}"

   async def main():
       # Create client and add all tools
       client = LLMClient("openai/gpt-4-turbo")
       client.add_tool(list_directory)
       client.add_tool(read_file)
       client.add_tool(search_files)
       client.add_tool(get_file_info)

       # Create agent
       agent = ReactAgent(client, max_iterations=10)

       # Run complex task that requires multiple tools
       result = await agent.run(
           "Find all Python files in the current directory, then read the contents "
           "of the largest one and tell me what it does.",
           verbose=True
       )

       print("\n" + "="*50)
       print("FINAL RESULT:")
       print("="*50)
       print(result)

   if __name__ == "__main__":
       asyncio.run(main())

Testing Your Tools
------------------

Test Tools Independently
~~~~~~~~~~~~~~~~~~~~~~~~

Before using tools with an agent, test them directly:

.. code-block:: python

   # Test the function works correctly
   def test_calculator():
       result = calculator("add", 5, 3)
       assert result == 8, f"Expected 8, got {result}"

       result = calculator("divide", 10, 2)
       assert result == 5, f"Expected 5, got {result}"

       # Test error handling
       result = calculator("divide", 10, 0)
       assert "error" in result.lower(), "Should return error for division by zero"

       print("All tests passed!")

   test_calculator()

Test with LLMClient
~~~~~~~~~~~~~~~~~~~

Test how the LLM uses your tools:

.. code-block:: python

   async def test_tool_with_llm():
       client = LLMClient("openai/gpt-4-turbo")
       client.add_tool(calculator)

       # Test that LLM correctly calls the tool
       response = await client.invoke("What is 25 multiplied by 4?")
       print(response.message.content)

       # Verify the answer is correct
       assert "100" in response.message.content

   asyncio.run(test_tool_with_llm())

Common Pitfalls and Solutions
------------------------------

Pitfall 1: Missing Type Hints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: python

   def bad_tool(query, max_results):  # No type hints!
       """Search for items."""
       return []

**Solution:**

.. code-block:: python

   def good_tool(query: str, max_results: int) -> list[str]:
       """Search for items."""
       return []

Pitfall 2: Vague Parameter Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: python

   def process(data: str, flag: bool) -> str:
       """Process data."""  # What is 'data'? What does 'flag' do?
       pass

**Solution:**

.. code-block:: python

   def format_address(
       address_string: str,
       include_country: bool
   ) -> str:
       """Format a postal address for display.

       Args:
           address_string: Raw address text with comma-separated components
           include_country: If True, includes country name in formatted output
       """
       pass

Pitfall 3: Returning Complex Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: python

   def get_user(user_id: str) -> User:  # Custom class not JSON-serializable
       """Get user object."""
       return User(id=user_id, name="Alice")

**Solution:**

.. code-block:: python

   def get_user(user_id: str) -> dict:
       """Get user information as a dictionary.

       Returns:
           Dictionary with keys: id, name, email, created_at
       """
       return {
           "id": user_id,
           "name": "Alice",
           "email": "alice@example.com",
           "created_at": "2024-01-01"
       }

Pitfall 4: Silent Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:**

.. code-block:: python

   def delete_file(filepath: str) -> bool:
       """Delete a file."""
       try:
           os.remove(filepath)
           return True
       except:
           return False  # LLM doesn't know WHY it failed

**Solution:**

.. code-block:: python

   def delete_file(filepath: str) -> str:
       """Delete a file from the filesystem.

       Args:
           filepath: Path to the file to delete

       Returns:
           Success message if deleted, or specific error message explaining
           why deletion failed (e.g., file not found, permission denied).
       """
       try:
           os.remove(filepath)
           return f"Successfully deleted {filepath}"
       except FileNotFoundError:
           return f"Error: File {filepath} does not exist"
       except PermissionError:
           return f"Error: Permission denied to delete {filepath}"
       except Exception as e:
           return f"Error deleting file: {str(e)}"

Best Practices Summary
----------------------

1. **Always include type hints** for all parameters and return values
2. **Write detailed docstrings** that explain what, when, and how
3. **Document parameter formats** and valid values clearly
4. **Return strings or JSON-serializable types** only
5. **Handle errors gracefully** and return informative error messages
6. **Test tools independently** before using with agents
7. **Use descriptive parameter names** that explain their purpose
8. **Document side effects** prominently in the docstring
9. **Provide examples** in docstrings for complex tools
10. **Keep tools focused** - one tool should do one thing well

Next Steps
----------

* Learn about :doc:`../api` for detailed API reference
* Explore :doc:`configure_providers` to set up different LLM providers
* Check out the :doc:`../quickstart` for complete examples
* Build a :ref:`ReactAgent <python_agents.agents.ReactAgent>` to chain multiple tool calls together
