Configure LLMClient for Different Providers
============================================

The ``LLMClient`` class is designed to work with any OpenAI-compatible API endpoint. By default, it uses OpenRouter, but you can easily configure it to work with OpenAI, Anthropic, or any other compatible provider.

OpenRouter (Default)
--------------------

OpenRouter is the default provider and provides access to multiple models through a single API endpoint.

Setup
~~~~~

1. Get an API key from `OpenRouter <https://openrouter.ai/>`_
2. Set the environment variable:

.. code-block:: bash

   export OPENAI_API_KEY="your-openrouter-api-key"

Usage
~~~~~

.. code-block:: python

   from python_agents.client import LLMClient
   import asyncio

   async def main():
       # Uses OpenRouter by default
       client = LLMClient("openai/gpt-4-turbo")
       response = await client.invoke("Hello!")
       print(response.message.content)

   asyncio.run(main())

Available models on OpenRouter see `OpenRouter models <https://openrouter.ai/models>`_

OpenAI
------

To use OpenAI's API directly, configure the base URL to point to OpenAI's endpoint.

Setup
~~~~~

1. Get an API key from `OpenAI <https://platform.openai.com/>`_
2. Set the environment variable:

.. code-block:: bash

   export OPENAI_API_KEY="sk-your-openai-api-key"

Usage
~~~~~

.. code-block:: python

   from python_agents.client import LLMClient
   import asyncio

   async def main():
       # Configure for OpenAI
       client = LLMClient(
           model_name="gpt-4-turbo",
           base_url="https://api.openai.com/v1"
       )
       response = await client.invoke("What is 2+2?")
       print(response.message.content)

   asyncio.run(main())

Available OpenAI models: see `OpenAI models documentation <https://platform.openai.com/docs/models>`_ 

Custom Providers
----------------

Any OpenAI-compatible API endpoint can be used with ``LLMClient``. Here's a template:

.. code-block:: python

   from python_agents.client import LLMClient
   import asyncio

   async def main():
       client = LLMClient(
           model_name="your-model-name",
           base_url="https://your-provider.com/v1"
       )

       # Set the API key via environment variable:
       # export OPENAI_API_KEY="your-api-key"

       response = await client.invoke("Test query")
       print(response.message.content)

   asyncio.run(main())

Environment Variables
---------------------

The ``LLMClient`` uses the ``OPENAI_API_KEY`` environment variable for authentication across all providers:

.. code-block:: bash

   # For OpenRouter
   export OPENAI_API_KEY="your-openrouter-key"

   # For OpenAI
   export OPENAI_API_KEY="sk-your-openai-key"

   # For custom providers
   export OPENAI_API_KEY="your-custom-provider-key"

You can also load environment variables from a ``.env`` file:

.. code-block:: python

   from dotenv import load_dotenv
   from python_agents.client import LLMClient

   load_dotenv()  # Loads variables from .env file

   client = LLMClient("openai/gpt-4-turbo")

Example ``.env`` file:

.. code-block:: text

   OPENAI_API_KEY=your-api-key-here

Next Steps
----------

* Learn about :doc:`../api` for detailed API reference
* Explore tool calling in the :doc:`../quickstart` guide
* Build complex agents with ``ReactAgent``
