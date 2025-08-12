from fastmcp import FastMCP

server = FastMCP("Demo")

@server.tool()
async def greet_user(name:str) -> str:
    """
    A tool that returns a greeting message
    Args:
        name: The name of the person to greet.
    Returns:
        str: A greeting message for the given name.
    """
    return f"Hello {name}, how are you today?"

if __name__ == "__main__":
    server.run(transport="sse")