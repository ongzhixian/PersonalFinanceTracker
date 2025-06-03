"""MCP Server to Conduit
"""
import asyncio
import json
from fastmcp import FastMCP
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.routing import Mount
from conduit_client import AsyncOpenAI
import uvicorn

import pdb

URI_SCHEME = 'conduit-mcp'

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
    uri=f"{URI_SCHEME}://models",      # Explicit URI (required)
    name="Models",          # Custom name
    description="Return available model ID list.", # Custom description
    mime_type="application/json",             # Explicit MIME type
    tags={"resource"}                     # Categorization tags
)
async def get_models():
    """Return available model IDs"""
    client = AsyncOpenAI()
    json_response = await client.models.list()
    return [ model.id for model in json_response.data ]

#
# # Resource returning JSON data (dict is auto-serialized)
# @mcp.resource("data://config")
# def get_config() -> dict:
#     """Provides application configuration as JSON."""
#     return {
#         "theme": "dark",
#         "version": "1.2.0",
#         "features": ["tools", "resources"],
#     }
#
# @mcp.resource(
#     uri="data://app-status",      # Explicit URI (required)
#     name="ApplicationStatus",     # Custom name
#     description="Provides the current status of the application.", # Custom description
#     mime_type="application/json", # Explicit MIME type
#     tags={"monitoring", "status"} # Categorization tags
# )
# def get_application_status() -> dict:
#     """Internal function description (ignored if description is provided above)."""
#     return {"status": "ok", "uptime": 12345, "version": mcp.settings.version} # Example usage

###
#
# import json
#
# from mcp.server.fastmcp import FastMCP, Context
# from mcp.server.fastmcp.prompts import base
#
# mcp = FastMCP("Sample Server")
#
# # RESOURCES
#
# ## STATIC RESOURCES
#
# @mcp.resource("resource://app-configuration")
# def get_config() -> str:
#     """Static application configuration data"""
#     return "App configuration here"
#
# @mcp.resource("resource://app-version")
# def get_version():
#     """Static application version label"""
#     return "1.0.1"

# def _get_mcp_config():
#     with open('conduit_mcp.json') as input_file:
#         return json.load(input_file)

class McpConfig(object):
    def __init__(self, configuration_json_file_path:str):
        with open(configuration_json_file_path) as input_file:
            self.json_configuration = json.load(input_file)

    def _get_configuration(self, colon_delimited_key: str, default=None, raise_on_missing=False):
        """
        Retrieve value from nested dict using colon-delimited key.
        If a key is missing, return `default` or raise KeyError if raise_on_missing is True.
        """
        keys = colon_delimited_key.split(':')
        value = self.json_configuration
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                if raise_on_missing:
                    raise KeyError(f"Key path '{colon_delimited_key}' not found at '{key}'")
                return default
        return value

    def get_mcp_transport_settings(self) -> dict:
        """
        1. mcp.run(transport="stdio") # Same mcp.run()
        2. mcp.run(transport="sse", host="127.0.0.1", port=4500)
        3. mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
        """
        transport_type = self._get_configuration('mcp:transport_type').lower()
        if transport_type == 'stdio':
            return {
                "transport" : "stdio"
            }
        else:

            transport_settings = self._get_configuration(f'mcp:{transport_type}')
            return {
                "transport": transport_type,
                "host": transport_settings['host'],
                "port": transport_settings['port'],
            }



def main():
    mcp_config = McpConfig('./conduit_mcp.json')
    mcp_transport_settings = mcp_config.get_mcp_transport_settings()
    mcp.run(**mcp_transport_settings)

    # Get a Starlette app instance for Streamable HTTP transport (recommended)
    # mcp_app = mcp.http_app(path='/mcp')
    # mcp_app = mcp.streamable_http_app(path='/mcp')
    #
    # # Create a Starlette app and mount the MCP server
    # app = Starlette(
    #     routes=[
    #         Mount('/mcp-server', app=mcp_app),
    #         # Add other routes as needed
    #     ],
    #     lifespan=mcp_app.router.lifespan_context,
    # )
    # uvicorn.run(app, host="0.0.0.0", port=4500)

if __name__ == "__main__":
    main()
