import json

from openai import AsyncOpenAI

from python_agents import tools
from python_agents.message import Message


class LLMClient:
    def __init__(
        self,
        model_name: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        self.model_name = model_name
        self.client = AsyncOpenAI(base_url=base_url)
        self.tools = {}

    def add_tool(self, func):
        schema = tools.create_tool_schema(func)
        self.tools[func.__name__] = {"func": func, "schema": schema}

    async def _make_llm_call(self, messages: list[Message], model_name: str = None):
        available_tools = [tool["schema"] for tool in self.tools.values()]

        response = await self.client.chat.completions.create(
            model=model_name or self.model_name,
            messages=messages,
            tools=available_tools,
        )

        return response.choices[0]

    async def _make_tool_call(self, tc):
        tool_name = tc.function.name
        tool_args = tc.function.arguments
        tool_args = json.loads(tool_args) if tool_args else {}

        if tool_name in self.tools:
            func = self.tools[tool_name]["func"]
            tool_result = str(func(**tool_args))
        else:
            raise RuntimeError(f"LLM tried to call unknown tool '{tool_name}'")
        return tc.id, tool_name, tool_result

    async def invoke(self, query: list[Message] | Message | str, model_name=None, verbose: bool = False):
        if type(query) is str:
            messages = [Message(role="user", content=query)]
        elif type(query) is Message:
            messages = [query]
        elif type(query) is list:
            messages = query
        else:
            raise ValueError("Parameter query is of wrong type!")

        response = await self._make_llm_call(messages, model_name)

        if response.message.tool_calls is not None:
            messages.append(response.message.model_dump())
            for tc in response.message.tool_calls:
                tool_call_id, tool_name, tool_result = await self._make_tool_call(tc)
                print(f"🤖 Called tool {tool_name}")

                tool_message = Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call_id,
                    name=tool_name,
                )
                messages.append(tool_message)

            response = await self._make_llm_call(messages, model_name)
        else:
            if verbose:
                print(f"🤖 Response: {response.message.content}")

        return response
