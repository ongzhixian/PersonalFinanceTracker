"""
MCP Integration Module for Gemini AI Agent
Provides Model Context Protocol server and client functionality
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import httpx
from datetime import datetime

try:
    from fastmcp import FastMCP, Context
    from mcp import ClientSession, StdioServerTransport
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
except ImportError as e:
    print(f"Missing MCP dependencies: {e}")
    print("Please install: pip install fastmcp mcp")
    exit(1)

from gemini_agent import GeminiAgent

# Configure logging
logger = logging.getLogger(__name__)


class GeminiMCPServer:
    """MCP Server that exposes Gemini AI Agent capabilities"""
    
    def __init__(self, agent: GeminiAgent, server_name: str = "GeminiMCPServer"):
        """
        Initialize the Gemini MCP Server
        
        Args:
            agent: GeminiAgent instance
            server_name: Name of the MCP server
        """
        self.agent = agent
        self.server_name = server_name
        self.mcp = FastMCP(
            name=server_name,
            instructions="""
            Gemini AI Agent MCP Server provides access to Google's Gemini AI models
            with multi-context conversation management, image generation/analysis,
            and document processing capabilities.
            """
        )
        self._setup_resources()
        self._setup_tools()
    
    def _setup_resources(self):
        """Setup MCP resources"""
        
        @self.mcp.resource(
            uri="gemini://agent/stats",
            name="Agent Statistics",
            description="Current usage statistics and session information",
            mime_type="application/json"
        )
        def get_agent_stats():
            """Get agent statistics"""
            return json.dumps(self.agent.get_stats(), indent=2)
        
        @self.mcp.resource(
            uri="gemini://sessions/list",
            name="Session List",
            description="List all conversation sessions",
            mime_type="application/json"
        )
        def get_sessions():
            """Get all sessions"""
            return json.dumps(self.agent.list_sessions(), indent=2)
        
        @self.mcp.resource(
            uri="gemini://session/{session_name}/context",
            name="Session Context",
            description="Get context from a specific session",
            mime_type="text/plain"
        )
        def get_session_context(session_name: str, ctx: Context) -> str:
            """Get formatted context from a session"""
            return self.agent.get_session_context(session_name)
        
        @self.mcp.resource(
            uri="gemini://models/available",
            name="Available Models",
            description="List of available Gemini models",
            mime_type="application/json"
        )
        def get_available_models():
            """Get available models"""
            return json.dumps(self.agent.models, indent=2)
    
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.mcp.tool()
        def generate_text(prompt: str, 
                         temperature: float = 0.7, 
                         max_tokens: int = 1024,
                         session_name: Optional[str] = None) -> str:
            """
            Generate text using Gemini AI
            
            Args:
                prompt: Text prompt for generation
                temperature: Sampling temperature (0.0-1.0)
                max_tokens: Maximum tokens in response
                session_name: Optional session to use
            """
            try:
                if session_name:
                    # Switch to session temporarily
                    original_session = self.agent.current_session
                    if session_name not in self.agent.conversation_sessions:
                        self.agent.create_session(session_name)
                    self.agent.switch_session(session_name)
                    
                    result = self.agent.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
                    
                    # Switch back to original session
                    self.agent.switch_session(original_session)
                    return result
                else:
                    return self.agent.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
            except Exception as e:
                return f"Error generating text: {str(e)}"
        
        @self.mcp.tool()
        def chat(message: str, 
                session_name: Optional[str] = None,
                maintain_context: bool = True,
                context_sources: Optional[List[str]] = None) -> str:
            """
            Have a conversation with Gemini
            
            Args:
                message: User message
                session_name: Session to use for conversation
                maintain_context: Whether to maintain conversation context
                context_sources: List of sessions to merge context from
            """
            try:
                return self.agent.chat(
                    message=message,
                    session_name=session_name,
                    maintain_context=maintain_context,
                    context_sources=context_sources
                )
            except Exception as e:
                return f"Error in chat: {str(e)}"
        
        @self.mcp.tool()
        def create_session(session_name: str, context_window: int = 10) -> str:
            """
            Create a new conversation session
            
            Args:
                session_name: Name for the new session
                context_window: Number of exchanges to maintain in context
            """
            try:
                result = self.agent.create_session(session_name, context_window)
                return f"Created session '{result}' with context window {context_window}"
            except Exception as e:
                return f"Error creating session: {str(e)}"
        
        @self.mcp.tool()
        def switch_session(session_name: str) -> str:
            """
            Switch to a different conversation session
            
            Args:
                session_name: Name of session to switch to
            """
            try:
                success = self.agent.switch_session(session_name)
                if success:
                    return f"Switched to session '{session_name}'"
                else:
                    return f"Session '{session_name}' does not exist"
            except Exception as e:
                return f"Error switching session: {str(e)}"
        
        @self.mcp.tool()
        def analyze_image(image_path: str, prompt: str = "Describe this image in detail") -> str:
            """
            Analyze an image using Gemini Vision
            
            Args:
                image_path: Path to image file
                prompt: Analysis prompt
            """
            try:
                return self.agent.analyze_image(image_path, prompt)
            except Exception as e:
                return f"Error analyzing image: {str(e)}"
        
        @self.mcp.tool()
        def generate_image(prompt: str, save_path: Optional[str] = None) -> str:
            """
            Generate an image using Gemini
            
            Args:
                prompt: Image generation prompt  
                save_path: Optional path to save image
            """
            try:
                return self.agent.generate_image(prompt, save_path)
            except Exception as e:
                return f"Error generating image: {str(e)}"
        
        @self.mcp.tool()
        def process_document(file_path: str, question: str = "Summarize this document") -> str:
            """
            Process and analyze a document
            
            Args:
                file_path: Path to document file
                question: Question about the document
            """
            try:
                return self.agent.process_document(file_path, question)
            except Exception as e:
                return f"Error processing document: {str(e)}"
        
        @self.mcp.tool()
        def merge_session_contexts(session_names: List[str], max_entries: int = 20) -> str:
            """
            Merge context from multiple sessions
            
            Args:
                session_names: List of session names to merge
                max_entries: Maximum number of entries to include
            """
            try:
                return self.agent.merge_contexts(session_names, max_entries)
            except Exception as e:
                return f"Error merging contexts: {str(e)}"
        
        @self.mcp.tool()
        def create_contextual_summary(session_names: Optional[List[str]] = None, 
                                    max_entries: int = 50) -> str:
            """
            Create a summary of conversation context across sessions
            
            Args:
                session_names: Sessions to summarize (all if None)
                max_entries: Maximum entries to include
            """
            try:
                return self.agent.create_contextual_summary(session_names, max_entries)
            except Exception as e:
                return f"Error creating summary: {str(e)}"
        
        @self.mcp.tool()
        def export_session(session_name: str, format_type: str = "json") -> str:
            """
            Export session context to file
            
            Args:
                session_name: Session to export
                format_type: Export format (json, txt, md)
            """
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{session_name}_export_{timestamp}.{format_type}"
                self.agent.export_session_context(session_name, file_path, format_type)
                return f"Session exported to: {file_path}"
            except Exception as e:
                return f"Error exporting session: {str(e)}"
        
        @self.mcp.tool()
        def set_system_instruction(instruction: str) -> str:
            """
            Set system instruction for the agent
            
            Args:
                instruction: New system instruction
            """
            try:
                self.agent.set_system_instruction(instruction)
                return f"System instruction updated: {instruction[:50]}..."
            except Exception as e:
                return f"Error setting system instruction: {str(e)}"


class GeminiMCPClient:
    """MCP Client that can connect to other MCP servers and use their tools/resources"""
    
    def __init__(self, agent: GeminiAgent):
        """
        Initialize the Gemini MCP Client
        
        Args:
            agent: GeminiAgent instance
        """
        self.agent = agent
        self.connections: Dict[str, Any] = {}
        self.available_tools: Dict[str, List[Tool]] = {}
        self.available_resources: Dict[str, List[Any]] = {}
    
    async def connect_to_server(self, server_name: str, transport_config: Dict[str, Any]) -> bool:
        """
        Connect to an MCP server
        
        Args:
            server_name: Name to identify the server
            transport_config: Transport configuration
            
        Returns:
            True if connection successful
        """
        try:
            if transport_config.get("type") == "stdio":
                # Stdio transport
                transport = StdioServerTransport(
                    command=transport_config["command"],
                    args=transport_config.get("args", [])
                )
            elif transport_config.get("type") == "http":
                # HTTP transport (custom implementation needed)
                # This is a placeholder - actual implementation would depend on server
                logger.warning("HTTP transport not yet fully implemented")
                return False
            else:
                logger.error(f"Unsupported transport type: {transport_config.get('type')}")
                return False
            
            # Create session
            session = ClientSession(transport)
            await session.initialize()
            
            # Store connection
            self.connections[server_name] = {
                "session": session,
                "transport": transport,
                "config": transport_config
            }
            
            # Get available tools and resources
            tools_result = await session.list_tools()
            self.available_tools[server_name] = tools_result.tools
            
            resources_result = await session.list_resources()
            self.available_resources[server_name] = resources_result.resources
            
            logger.info(f"Connected to MCP server '{server_name}'")
            logger.info(f"Available tools: {len(self.available_tools[server_name])}")
            logger.info(f"Available resources: {len(self.available_resources[server_name])}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to server '{server_name}': {str(e)}")
            return False
    
    async def disconnect_from_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.connections:
            try:
                connection = self.connections[server_name]
                await connection["session"].close()
                del self.connections[server_name]
                if server_name in self.available_tools:
                    del self.available_tools[server_name]
                if server_name in self.available_resources:
                    del self.available_resources[server_name]
                logger.info(f"Disconnected from server '{server_name}'")
            except Exception as e:
                logger.error(f"Error disconnecting from '{server_name}': {str(e)}")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on an MCP server
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result as string
        """
        try:
            if server_name not in self.connections:
                return f"Not connected to server '{server_name}'"
            
            session = self.connections[server_name]["session"]
            result = await session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if result.content:
                text_results = []
                for content in result.content:
                    if isinstance(content, TextContent):
                        text_results.append(content.text)
                return "\n".join(text_results)
            
            return "Tool executed successfully (no text output)"
            
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on '{server_name}': {str(e)}")
            return f"Error calling tool: {str(e)}"
    
    async def get_resource(self, server_name: str, resource_uri: str) -> str:
        """
        Get a resource from an MCP server
        
        Args:
            server_name: Name of the server
            resource_uri: URI of the resource
            
        Returns:
            Resource content as string
        """
        try:
            if server_name not in self.connections:
                return f"Not connected to server '{server_name}'"
            
            session = self.connections[server_name]["session"]
            result = await session.read_resource(resource_uri)
            
            # Extract content from result
            if result.contents:
                text_results = []
                for content in result.contents:
                    if hasattr(content, 'text'):
                        text_results.append(content.text)
                    elif hasattr(content, 'data'):
                        text_results.append(f"[Binary data: {len(content.data)} bytes]")
                return "\n".join(text_results)
            
            return "Resource retrieved (no content)"
            
        except Exception as e:
            logger.error(f"Error getting resource '{resource_uri}' from '{server_name}': {str(e)}")
            return f"Error getting resource: {str(e)}"
    
    def list_available_tools(self, server_name: str = None) -> Dict[str, List[str]]:
        """
        List available tools from connected servers
        
        Args:
            server_name: Specific server name (all if None)
            
        Returns:
            Dictionary of server names to tool lists
        """
        if server_name:
            if server_name in self.available_tools:
                return {server_name: [tool.name for tool in self.available_tools[server_name]]}
            else:
                return {server_name: []}
        else:
            return {
                name: [tool.name for tool in tools] 
                for name, tools in self.available_tools.items()
            }
    
    def list_available_resources(self, server_name: str = None) -> Dict[str, List[str]]:
        """
        List available resources from connected servers
        
        Args:
            server_name: Specific server name (all if None)
            
        Returns:
            Dictionary of server names to resource lists
        """
        if server_name:
            if server_name in self.available_resources:
                return {server_name: [resource.uri for resource in self.available_resources[server_name]]}
            else:
                return {server_name: []}
        else:
            return {
                name: [resource.uri for resource in resources] 
                for name, resources in self.available_resources.items()
            }
    
    async def chat_with_mcp_context(self, message: str, server_tools: Dict[str, List[str]] = None) -> str:
        """
        Chat with Gemini using context from MCP servers
        
        Args:
            message: User message
            server_tools: Dictionary of server_name -> [tool_names] to call for context
            
        Returns:
            AI response with MCP context
        """
        try:
            mcp_context = {}
            
            if server_tools:
                for server_name, tool_names in server_tools.items():
                    if server_name in self.connections:
                        server_context = {}
                        for tool_name in tool_names:
                            # Call tool with no arguments (for context tools)
                            result = await self.call_tool(server_name, tool_name, {})
                            server_context[tool_name] = result
                        mcp_context[server_name] = server_context
            
            # Use Gemini agent with MCP context
            return self.agent.chat(
                message=message,
                external_context={"mcp_servers": mcp_context}
            )
            
        except Exception as e:
            logger.error(f"Error in MCP context chat: {str(e)}")
            return f"Error: {str(e)}"


class GeminiMCPIntegration:
    """Main integration class that combines server and client functionality"""
    
    def __init__(self, agent: GeminiAgent = None):
        """
        Initialize the MCP integration
        
        Args:
            agent: GeminiAgent instance (creates new one if None)
        """
        self.agent = agent or GeminiAgent()
        self.server = GeminiMCPServer(self.agent)
        self.client = GeminiMCPClient(self.agent)
        self.server_configs: Dict[str, Dict[str, Any]] = {}
    
    def get_mcp_server(self) -> FastMCP:
        """Get the FastMCP server instance"""
        return self.server.mcp
    
    async def connect_to_servers(self, config_file: str = None, configs: Dict[str, Dict[str, Any]] = None):
        """
        Connect to multiple MCP servers
        
        Args:
            config_file: Path to JSON config file
            configs: Dictionary of server configurations
        """
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
        
        if not configs:
            logger.warning("No server configurations provided")
            return
        
        self.server_configs = configs
        
        for server_name, config in configs.items():
            success = await self.client.connect_to_server(server_name, config)
            if success:
                logger.info(f"Connected to MCP server: {server_name}")
            else:
                logger.error(f"Failed to connect to MCP server: {server_name}")
    
    async def disconnect_all_servers(self):
        """Disconnect from all MCP servers"""
        for server_name in list(self.client.connections.keys()):
            await self.client.disconnect_from_server(server_name)
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about the MCP integration"""
        return {
            "agent_stats": self.agent.get_stats(),
            "connected_servers": list(self.client.connections.keys()),
            "available_tools": self.client.list_available_tools(),
            "available_resources": self.client.list_available_resources(),
            "server_configs": list(self.server_configs.keys())
        }


# Utility functions for easy setup
def create_mcp_server_config(host: str = "127.0.0.1", 
                           port: int = 3000, 
                           path: str = "/mcp") -> Dict[str, Any]:
    """Create a basic MCP server configuration"""
    return {
        "mcp": {
            "transport_type": "streamable-http",
            "streamable-http": {
                "host": host,
                "port": port,
                "path": path
            }
        },
        "uvicorn": {
            "host": host,
            "port": port
        },
        "fastapi": {
            "root_path": path
        }
    }


def create_stdio_client_config(command: str, args: List[str] = None) -> Dict[str, Any]:
    """Create a stdio client configuration"""
    return {
        "type": "stdio",
        "command": command,
        "args": args or []
    }


async def run_mcp_server(integration: GeminiMCPIntegration, 
                        host: str = "127.0.0.1", 
                        port: int = 3000):
    """Run the MCP server"""
    import uvicorn
    
    # Get the FastMCP app
    app = integration.get_mcp_server()
    
    # Run the server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create integration
        integration = GeminiMCPIntegration()
        
        # Run server in background (you'd typically do this in a separate process)
        # await run_mcp_server(integration)
        
        # Example client usage
        print("MCP Integration initialized")
        print(f"Stats: {integration.get_integration_stats()}")
    
    asyncio.run(main())
