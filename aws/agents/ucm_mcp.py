import json
import sys

from fastapi import FastAPI
from fastmcp import FastMCP, Context
import uvicorn

from shared_mcp import get_mcp_client_logger, McpServerJsonConfiguration

# HACK PYTHONPATH to include parent path (so we can import shared_counter)
sys.path.append('..')
print('sys.path', sys.path)
from shared_counter import CounterRepository

import pdb

mcp_config = McpServerJsonConfiguration('./ucm_mcp.json')
log = get_mcp_client_logger()

URI_SCHEME = 'ucm-mcp'

mcp = FastMCP(
    name="UcmMcp",
    instructions="""
    Provides information about Ucm.
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
    return "1.0.0"

@mcp.resource(
    uri=f"{URI_SCHEME}://counter-name",      # Explicit URI (required)
    name="Counter Name List",                # Custom name
    description="Get a list of all counter names.", # Custom description
    mime_type="application/json",             # Explicit MIME type
    tags={"status"}                     # Categorization tags
)
def get_all_counter_names():
    """Version number of this MCP server"""
    counter_repository = CounterRepository()
    operation_result_message = counter_repository.get_counter_name_list()
    return operation_result_message.data_object
    # pdb.set_trace()
    # return json.dumps(counter_repository.get_counter_name_list())

@mcp.resource(
    uri=f"{URI_SCHEME}://counter",      # Explicit URI (required)
    name="Counter List",                # Custom name
    description="Get a list of all counters.", # Custom description
    mime_type="application/json",             # Explicit MIME type
    tags={"status"}                     # Categorization tags
)
def get_all_counters():
    """Version number of this MCP server"""
    counter_repository = CounterRepository()
    operation_result_message = counter_repository.get_counter_name_list()
    return operation_result_message.data_object
    # pdb.set_trace()
    # return json.dumps(counter_repository.get_counter_name_list())

## counter, configuration, note, user_credential

@mcp.resource(
    uri=f"{URI_SCHEME}://counter/{{name}}",
    name="Counter",
    description="Retrieve the counter for the given name.",
    mime_type="application/json",
    tags={"resource"}
)
async def get_counter(name: str) -> dict:
    """Get details for a specific name."""
    counter_repository = CounterRepository()
    operation_result_message = counter_repository.get_counter(name)
    return operation_result_message.data_object


# TOOLS

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b + 10

########################################
# Main scripts

def main_fastapi(mcp:FastMCP, mcp_config: McpServerJsonConfiguration):
    # Mount the MCP app as a sub-application
    mcp_app = mcp.http_app()

    # Create FastAPI app
    app = FastAPI(
        title="Ucm MCP Service",
        description="A service that data about Ucm",
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
            "service": "Ucm MCP Service",
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
