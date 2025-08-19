from fastmcp import FastMCP

URI_SCHEME = 'ucm-mcp'

mcp = FastMCP(
    name="UCM MCP Server",
    instructions="""
    UCM Model Context Protocol Server providing UCM service integration.
    
    This server provides tools and resources for interacting with various UCM services including:
    - Configuration management
    - User management
    
    All operations respect UCM permissions and will fail gracefully if credentials are not configured.
    """)

########################################
# STATIC RESOURCES
########################################

@mcp.resource(
    uri=f"{URI_SCHEME}://version",
    name="UCM MCP Server Version",
    description="Returns the version of this UCM MCP server",
    mime_type="text/plain",
    tags={"info", "version"}
)
def get_version():
    """Get server version"""
    return "1.0.0"


########################################
# S3 TOOLS
########################################

@mcp.tool()
def list_configuration():
    """List all UCM configurations"""
    try:
        configurations = {
            'config1': 'value1',
            'config2': 'value2',
            'config3': 'value3'
        }
        return {
            "configurations": configurations,
            "count": len(configurations)
        }
    except Exception as e:
        return {"error": str(e), "configurations": []}


@mcp.tool()
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
    mcp.run(transport="sse")