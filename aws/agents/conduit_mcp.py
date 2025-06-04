from fastapi import FastAPI
from fastmcp import FastMCP, Context
import uvicorn

from conduit_client import AsyncOpenAI

from shared_mcp import get_mcp_client_logger, McpServerJsonConfiguration, IdleTimeoutManager

URI_SCHEME = 'conduit-mcp'
mcp_config = McpServerJsonConfiguration('./conduit_mcp.json')
log = get_mcp_client_logger()


def save_state():
    """
    Implement your state-saving logic here.
    This function will be called before the process exits due to idle timeout.
    """
    print("[SAVE STATE] Saving state before exit...")
    # Example: Save to a file (replace with your actual logic)
    with open("server_state.txt", "w") as f:
        f.write("State saved at idle timeout.\n")
    print("[SAVE STATE] State saved.")

idle_timeout = IdleTimeoutManager(timeout_seconds=300, on_timeout=save_state)

mcp = FastMCP(
    name="ConduitMcp",
    instructions="""
    Provides information about Conduit.
    """)

# STATIC RESOURCES

@mcp.resource(
    uri=f"{URI_SCHEME}://version",      # Explicit URI (required)
    name="Application Version",          # Custom name
    description="Returns the version of this server application.", # Custom description
    mime_type="plain/text",             # Explicit MIME type
    tags={"status"}                     # Categorization tags
)
def get_version():
    """Version number of this MCP server"""
    return "1.0.1"

@mcp.resource(
    uri=f"{URI_SCHEME}://models",       # Explicit URI (required)
    name="Models",                      # Custom name
    description="Return available model ID list.", # Custom description
    mime_type="application/json",       # Explicit MIME type
    tags={"resource"}                   # Categorization tags
)
async def get_models():
    """Return available model IDs"""
    client = AsyncOpenAI()
    json_response = await client.models.list()
    return [ model.id for model in json_response.data ]

@mcp.resource(
    uri=f"{URI_SCHEME}://user-profile/{{name}}",
    name="User Profile",
    description="Return user profile for name.",
    mime_type="plain/text",
    tags={"resource"}
)
async def get_details(name: str, ctx: Context) -> dict:
    """Get details for a specific name."""
    return {
        "name": name,
        "accessed_at": ctx.request_id
    }

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b + 10

########################################
# Main scripts

def main_fastapi(mcp:FastMCP, mcp_config: McpServerJsonConfiguration):
    # Mount the MCP app as a sub-application
    mcp_app = mcp.http_app()

    # Create FastAPI app
    app = FastAPI(
        title="Conduit MCP Service",
        description="A service that data about Conduit",
        version="1.0.0",
        lifespan=mcp_app.lifespan
    )

    fastapi_settings = mcp_config.get_fastapi_settings()
    fastapi_root_path = fastapi_settings['root_path'] if 'root_path' in fastapi_settings else "/mcp-server"
    print(f'fastapi_root_path: {fastapi_root_path}')
    app.mount(fastapi_root_path, mcp_app, "mcp_application")

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint showing service information."""
        return {
            "service": "Conduit MCP Service",
            "version": "1.0.0",
            "status": "running",
        }

    # Health check endpoint
    @app.get("/health")
    async def get_health() -> dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "healthy"
        }

    uvicorn_settings = mcp_config.get_uvicorn_settings()
    uvicorn_settings_host = uvicorn_settings['host'] if 'host' in uvicorn_settings else '0.0.0.0'
    uvicorn_settings_port = uvicorn_settings['port'] if 'port' in uvicorn_settings else 4500
    uvicorn.run(app, host=uvicorn_settings_host, port=uvicorn_settings_port)
    # uvicorn server:app --reload

def main(mcp:FastMCP, mcp_config: McpServerJsonConfiguration):
    mcp_transport_settings = mcp_config.get_mcp_transport_settings()
    print('mcp_transport_settings', mcp_transport_settings)
    mcp.run(**mcp_transport_settings)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--Runtime", help="Runtime to use")
    #parser.add_argument("-o", "--Output", help="Show Output")

    known_args, unknown_args = parser.parse_known_args()
    runtime = known_args.Runtime

    if not runtime and unknown_args:
        # Parse first unknown arg as --Runtime
        arranged_args = ['--Runtime', unknown_args[0]]
        known_args, _ = parser.parse_known_args(arranged_args)
        runtime = known_args.Runtime

    runtime = runtime or 'standalone'
    print(f'Runtime: {runtime}')
    match runtime:
        case 'fastapi':
            main_fastapi(mcp, mcp_config)
        case _: # standalone
            main(mcp, mcp_config)
