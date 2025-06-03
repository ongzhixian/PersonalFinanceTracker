from fastapi import FastAPI
from fastmcp import FastMCP
import uvicorn

mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b + 10

# Mount the MCP app as a sub-application
mcp_app = mcp.streamable_http_app()

# Create FastAPI app

app = FastAPI(
    title="Test MCP Service",
    description="A test service that provides weather alerts and forecasts",
    version="1.0.0",
    lifespan=mcp_app.router.lifespan_context,
)

app.mount("/mcp-server", mcp_app, "mcp")

# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint showing service information."""
    return {
        "service": "Test MCP Service",
        "version": "1.0.0",
        "status": "running",
    }

# Health check endpoint
@app.get("/health")
async def get_health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

# uvicorn server:app --reload

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=4500)