import asyncio

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:4500/mcp-server/mcp") as client:
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())