"""
Echo MCP Server

Run MCP inspector (stdio) :
    mcp dev .\sample_server.py

In MCP Inspector, set the following if not using (uv):
    Command:    python.exe
    Arguments:  C:/Code/zong/pft/aws/agents/sample_server.py

Sections
    Resources
        Static
            get_config
            get_version
        Dynamic
            get_greeting
            get_profile
            echo_resource
    Tools
        add
        echo_tool
        greet
        get_weather
    Prompts
        echo_prompt
        summarize_request

"""
import json

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Sample Server")

# RESOURCES

## STATIC RESOURCES

@mcp.resource("resource://app-configuration")
def get_config() -> str:
    """Static application configuration data"""
    return "App configuration here"

@mcp.resource("resource://app-version")
def get_version():
    """Static application version label"""
    return "1.0.1"


## DYNAMIC RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    # Fetch profile for user_id...
    return {"name": f"User {user_id}", "status": "active"}

@mcp.resource("resource://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


# RESOURCE TEMPLATES

# @mcp.resource("echo://{message}")
# def echo_resource(message: str) -> str:
#     """Echo a message as a resource"""
#     return f"Resource echo: {message}"


# TOOLS

@mcp.tool(name="echo", description="echoes a message")
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message} (resource://{message})"


@mcp.tool()
def add(a: int, b: int, ctx: Context) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool()
def get_weather(city: str) -> float:
    """Get weather for specified city"""
    if city == 'Paris':
        return 11
    if city == 'Singapore':
        return 31
    if city == 'Sydney':
        return 18
    if city == 'Tokyo':
        return 25
    else:
        return 0
    #return f"Tool get_weather echo: {city}"


# def mcp_echo_tool():
#     """
#     A simple MCP tool that echoes a message based on user input.
#     """
#     # Prompt the user for a message
#     echo_message = input("Enter a message to echo: ")

#     # Echo the message back to the user
#     print(f"Echoed Message: {echo_message}")


# PROMPTS

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"

@mcp.prompt()
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]


if __name__ == "__main__":
    mcp_config = None
    with open('mcp_config.json') as input_file:
        mcp_config = json.load(input_file)

    transport_type = mcp_config['default']['transport_type']
    if transport_type == 'sse':
        #mcp.run(transport="sse", host="127.0.0.1", port=4500)
        mcp.run(transport="sse", port=4500)
    else: # Default to using stdio for transport
        #mcp.run(transport="stdio") # Same mcp.run()
        mcp.run()

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
