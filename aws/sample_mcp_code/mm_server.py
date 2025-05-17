"""
Echo MCP Server

Run MCP inspector (stdio) :
    mcp dev .\mcp_server.py

In MCP Inspector, set the following if not using (uv):
    Command:    python.exe
    Arguments:  C:/Code/zong/pft/aws/mcp_echo_server.py

"""
import json
from fastmcp import FastMCP

mcp = FastMCP("Echo Server")

# RESOURCES

@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"

# RESOURCE TEMPLATES

# @mcp.resource("echo://{message}")
# def echo_resource(message: str) -> str:
#     """Echo a message as a resource"""
#     return f"Resource echo: {message}"

# TOOLS

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

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

if __name__ == "__main__":
    mcp_config = None
    with open('mcp_config.json') as input_file:
        mcp_config = json.load(input_file)

    transport_type = mcp_config['default']['transport_type']
    if transport_type == 'sse':
        mcp.run(transport="sse", port=4500)
    else:
        # Runs using stdio for transport (default)
        mcp.run(transport="stdio") # Same mcp.run()