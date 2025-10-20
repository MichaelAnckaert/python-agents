from typing import Any, NotRequired, TypedDict


class Message(TypedDict):
    role: str
    content: str
    tool_call_id: NotRequired[str]
    name: NotRequired[str]
    tool_calls: NotRequired[list[Any]]
