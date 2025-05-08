# import asyncio
# from fastmcp import Client
#
# client = Client("./mcp_server.py")
#
# async def call_tool(name: str):
#     async with client:
#         result = await client.call_tool("greet", {"name": name})
#         print(result)
#
# asyncio.run(call_tool("Ford"))


import asyncio
from fastmcp import Client
from fastmcp.client.transports import SSETransport

async def example():
    async with Client(transport=SSETransport("http://127.0.0.1:4500/sse")) as client:
        await client.ping()
        result = await client.call_tool("greet", {"name": 'add'})
        print(result)
        result = await client.call_tool("greet", {"name": 'Prefect'})
        print(result)


if __name__ == "__main__":
    asyncio.run(example())