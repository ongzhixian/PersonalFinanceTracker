import json
import sys

from pydantic import Field
from fastapi import FastAPI
from fastmcp import FastMCP, Context
import uvicorn

from shared_mcp import get_mcp_client_logger, McpServerJsonConfiguration

# HACK PYTHONPATH to include parent path (so we can import shared_counter)
sys.path.append('..')
print('sys.path', sys.path)
from shared_counter import CounterRepository
from shared_user_credential import UserCredentialRepository
# from fastmcp.prompts.base import UserMessage, AssistantMessage

import pdb

mcp_config = McpServerJsonConfiguration('./ucm_mcp_config.json')
log = get_mcp_client_logger()

URI_SCHEME = 'ucm-mcp'

mcp = FastMCP(
    name="UcmMcp",
    instructions="""
    Provides information about Ucm.
    """)

# STATIC RESOURCES
from pathlib import Path
from fastmcp.resources import FileResource, TextResource, DirectoryResource

# Does not work :-(
# # 1. Exposing a static file directly
#
# readme_path = Path("./README.md").resolve()
# if readme_path.exists():
#     # Use a file:// URI scheme
#     readme_resource = FileResource(
#         # uri=f"file:///{readme_path.as_posix()}",
#         uri='file:///C:/Code/zong/pft/aws/agents/README.md',
#         path=readme_path, # Path to the actual file
#         name="README File",
#         description="The project's README.",
#         mime_type="text/markdown",
#         tags={"documentation"}
#     )
#     mcp.add_resource(readme_resource)



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
    description="Get a name only list of all counters.", # Custom description
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
    print('operation_result_message', operation_result_message)
    return operation_result_message.data_object


# FILE SYSTEM

@mcp.resource(
    uri=f"{URI_SCHEME}://file-content/{{filepath*}}",
    name="Get File Content",                            # Custom name
    description="Return file at the given filepath.",   # Custom description
    mime_type="text/plain",                       # Explicit MIME type
    tags={"content"}                                    # Categorization tags
)
def get_file_content(filepath: str) -> str:
    """Retrieves content at a file at specific filepath."""
    file_path = Path(filepath).resolve()
    file_resource = FileResource(
        uri=f"file://{file_path.as_posix()}",
        path=file_path,
        mime_type="text/markdown",
        tags={"file"}
    )
    return file_resource

@mcp.resource(
    uri=f"{URI_SCHEME}://file-list/{{directory_path*}}",
    name="Get File List",                               # Custom name
    description="List files of given directory path.",  # Custom description
    mime_type="application/json",                       # Explicit MIME type
    tags={"listing"}                                    # Categorization tags
)
def get_file_list(directory_path: str) -> str:
    """Retrieves list of file names found at specific directory path."""
    resolved_directory_path = Path(directory_path).resolve()
    directory_resource = DirectoryResource(
        uri=f"{URI_SCHEME}://file-list/{directory_path}",
        path=resolved_directory_path,
        name=f"Directory listing of {directory_path}",
        description=f"Lists files in {directory_path} directory.",
        recursive=True,
        tags={"file-listing"},
        mime_type="plain/text"
    )
    # print(directory_resource)
    return directory_resource


# TOOLS

def _get_content_by_mime_type(mime_type, content):
    norm_mime_type = mime_type.lower()
    match norm_mime_type:
        case 'application/json':
            return json.loads(content)
        case 'plain/text':
            return content
        case _:
            return None

def _handle_read_resource_response(response_list):
    print('read_resource_response', response_list)
    parsed_response_list = []
    for response in response_list:
        response_class_name = response.__class__.__name__.lower()
        match response_class_name:
            case 'readresourcecontents':
                return _get_content_by_mime_type(response.mime_type, response.content)
            case _:
                print("Unhandled read_resource_response_class_name:", response_class_name)
                return None

@mcp.tool(
    name="list_counters",               # Custom tool name for the LLM
    description="List all counters.",   # Custom description
    tags={"catalog", "list", "counters"},  # Optional tags for organization/filtering
    annotations={
        "title": "List All Counters",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
async def list_counters(ctx: Context):
    read_resource_response = await ctx.read_resource(f"{URI_SCHEME}://counter")
    #read_resource_response = [ReadResourceContents(content='[\n  "testCounter1",\n  "testCounter2"\n]', mime_type='application/json')]
    handled_response =  _handle_read_resource_response(read_resource_response)
    print('handled_response', handled_response)
    return handled_response
    #
    # print('read_resource_response', read_resource_response)
    # return read_resource_response


@mcp.tool(
    name="get_counter",  # Custom tool name for the LLM
    description="Get specific counter.",  # Custom description
    tags={"detail", "get", "counters"},  # Optional tags for organization/filtering
    annotations={
        "title": "Get Counter",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def get_counter(counter_name: str, ctx: Context):
    return ctx.read_resource(f"{URI_SCHEME}://counter/{counter_name}")


@mcp.tool(
    name="increment_counter",  # Custom tool name for the LLM
    description="Increment the value of specific counter by specified increment.",  # Custom description
    tags={"detail", "get", "counters"},  # Optional tags for organization/filtering
    annotations={
        "title": "Increment Counter",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True
    }
)
def increment_counter(counter_name: str, increment: int = 1):
    counter_repository = CounterRepository()
    operation_result_message = counter_repository.add_to_counter(counter_name, increment)
    return operation_result_message


# PROMPTS

@mcp.prompt(
    name="ReviewCode",  # Custom prompt name
    description="Review given code",  # Custom description
    tags={"analysis", "code", "review"}  # Optional categorization tags
)
def review_code(
        code: str = Field(description="The code to review")
    ) -> str:
    """"""
    return f"""Review the following code:\n\n```code\n{code}\n```\nProvide the code review as a markdown document.
    Provide grades for code for these categories: [Correctness, Readability, Efficiency, Maintainability, Style ] from 1 to 5."""

@mcp.prompt(
    name="GeneratePythonCode",  # Custom prompt name
    description="Generate Python code given a specification",  # Custom description
    tags={"code", "generation", "Python"}  # Optional categorization tags
)
def generate_python_code(
        specification: str = Field(description="Specification for the code to be generated.")
    ) -> str:
    """"""
    return f"""Given:\n\n```specification.md\n{specification}\n```\n\nGenerate code in Python."""


@mcp.prompt(
    name="InitializeQuery",  # Custom prompt name
    description="Executes query with knowledge of available MCP resources",  # Custom description
    tags={"query", "initialization"}  # Optional categorization tags
)
def query(
        mcp_resources: str = Field(description="List available MCP resources"),
        query: str = Field(description="List available MCP resources")
    ) -> str:
    """"""
    return f"Given following MCP resources:\n\n```\n{mcp_resources}\n```\n\n{query}"


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
