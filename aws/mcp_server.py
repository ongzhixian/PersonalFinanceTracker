import asyncio
from fastmcp import FastMCP, Client

mcp = FastMCP("My First MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

# For testing
# client = Client(mcp)
#
# async def call_tool(name: str):
#     async with client:
#         result = await client.call_tool("greet", {"name": name})
#         print(result)
#         result = await client.call_tool("greet", {"name": 'Prefect'})
#         print(result)
#
# asyncio.run(call_tool("Ford"))

if __name__ == "__main__":
    mcp.run(transport="sse", port=4500)
    # Runs using stdio for transport
    # mcp.run()
    # mcp.run(transport="stdio")