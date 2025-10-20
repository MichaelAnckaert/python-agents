# python-agents
Easy to use and powerful AI Agent development framework.

## Sample Usage
```python
client = LLMClient("openai/gpt-4.1-mini", memory=SimpleMemory())
response = await client.invoke("What is 1+1?")
print(response.message.content)

response = await client.invoke("And double that?")
print(response.message.content)
```


## Tool Calling
`python-agents` supports tool calling:

```code
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
    client = LLMClient("openai/gpt-4.1-mini", memory=SimpleMemory())
    client.add_tool(calculator)
    response = await client.invoke("What is 7+2 and what is 9*45? Use your calculator tool.")
    utils.pretty_print(client.memory.messages)
    print(response.message.content)
    response = await client.invoke("summarize all operations we did.")
    print(response.message.content)

```
