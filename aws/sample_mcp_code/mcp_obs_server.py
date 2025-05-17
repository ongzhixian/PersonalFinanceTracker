# server.py
from fastmcp import FastMCP, Context

# Create a server instance
mcp = FastMCP("Demo 🚀")

@mcp.tool()
def add(a: int, b: int, ctx: Context) -> int:
    """Add two numbers"""
    return a + b

# Static resource
@mcp.resource("config://version")
def get_version():
    return "2.0.1"

# Dynamic resource template
@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    # Fetch profile for user_id...
    return {"name": f"User {user_id}", "status": "active"}


@mcp.prompt()
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"

# Add this to server.py
if __name__ == "__main__":
    # Default: runs stdio transport
    mcp.run()

    # Example: Run with SSE transport on a specific port
    mcp.run(transport="sse", host="127.0.0.1", port=9000)


# Reference:
# https://apidog.com/blog/fastmcp/#how-to-install-fastmcp
# Running using FASTMCP CLI
# Run the server using stdio (default)
# fastmcp run my_server.py:mcp

# Run the server using Server-Sent Events (SSE) on port 8080
# fastmcp run my_server.py:mcp --transport sse --port 8080 --host 0.0.0.0

# Run with a different log level
# fastmcp run my_server.py:mcp --transport sse --log-level DEBUG

# Running
# fastmcp dev mcp_server.py
# Optionally add temporary dependencies
# fastmcp dev server.py --with pandas numpy
