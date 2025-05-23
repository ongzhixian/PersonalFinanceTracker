# Notes

## Running MCP Servers

There are several options for running a MCP server:

1. mcp.exe (MCP development tools)
   mcp run .\demo_mcp_server.py
2. fastmcp.exe (FastMCP CLI) -- this is likely a wrapper over mcp.exe (seeing they shared same arguments)
   fastmcp run .\demo_mcp_server.py
3. python.exe .\demo_mcp_server.py

To run Run a MCP server with the MCP Inspector, use dev argument instead run:
```
mcp run .\demo_mcp_server.py
fastmcp run .\demo_mcp_server.py:mcp
```

If the variable for your MCP server is not `mcp`, you would have suffixed it.
For example, instead of:
`mcp = FastMCP("Demo MCP Server")`
You defined it as:
`mcp_server = FastMCP("Demo MCP Server")`
Then to run, you would invoke:
`fastmcp run .\demo_mcp_server.py:mcp_server`


## MCP Inspector

In MCP Inspector, set the following if not using (uv):
Command:    python.exe
Arguments:  C:/Code/zong/pft/aws/agents/sample_server.py
