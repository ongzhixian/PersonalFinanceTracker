"""
Examples demonstrating Gemini AI Agent MCP Integration
Shows both server and client functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any
from gemini_mcp_integration import GeminiMCPIntegration, create_mcp_server_config, create_stdio_client_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_mcp_server():
    """Example: Running Gemini as an MCP Server"""
    print("🚀 MCP Server Example")
    print("=" * 50)
    
    # Create integration
    integration = GeminiMCPIntegration()
    
    # Get server stats
    stats = integration.get_integration_stats()
    print(f"📊 Integration Stats: {json.dumps(stats, indent=2)}")
    
    # The server exposes these tools via MCP:
    print("\n🛠️  Available MCP Tools:")
    tools = [
        "generate_text", "chat", "create_session", "switch_session",
        "analyze_image", "generate_image", "process_document",
        "merge_session_contexts", "create_contextual_summary",
        "export_session", "set_system_instruction"
    ]
    for tool in tools:
        print(f"   - {tool}")
    
    print("\n📁 Available MCP Resources:")
    resources = [
        "gemini://agent/stats",
        "gemini://sessions/list", 
        "gemini://session/{session_name}/context",
        "gemini://models/available"
    ]
    for resource in resources:
        print(f"   - {resource}")
    
    print("\n✅ MCP Server ready! Other MCP clients can now connect and use Gemini AI.")
    print("Example MCP client calls:")
    print('  - Call tool: {"method": "tools/call", "params": {"name": "chat", "arguments": {"message": "Hello!"}}}')
    print('  - Get resource: {"method": "resources/read", "params": {"uri": "gemini://agent/stats"}}')


async def example_mcp_client():
    """Example: Using Gemini as an MCP Client"""
    print("\n🔌 MCP Client Example")
    print("=" * 50)
    
    # Create integration
    integration = GeminiMCPIntegration()
    
    # Example server configurations
    server_configs = {
        "filesystem": create_stdio_client_config("npx", ["@modelcontextprotocol/server-filesystem", "/tmp"]),
        "git": create_stdio_client_config("npx", ["@modelcontextprotocol/server-git"]),
        # Add your own MCP servers here
    }
    
    print("🔗 Attempting to connect to MCP servers...")
    
    # Connect to servers (this would work if the servers are available)
    try:
        # await integration.connect_to_servers(configs=server_configs)
        print("⚠️  Skipping actual connections (servers not available in this example)")
        
        # Simulate available tools and resources
        integration.client.available_tools = {
            "filesystem": ["read_file", "write_file", "list_directory"],
            "git": ["get_status", "get_log", "get_diff"]
        }
        
        print("✅ Simulated connections established")
        print(f"📊 Available tools: {integration.client.list_available_tools()}")
        
        # Example of using MCP context in chat
        print("\n💬 Chatting with MCP context...")
        
        # This would use actual MCP tools if connected
        message = "What files are in the current directory and what's the git status?"
        
        # Simulate MCP context
        mcp_context = {
            "filesystem": {
                "list_directory": "file1.py\nfile2.md\nREADME.md",
                "read_file": "Content of important file..."
            },
            "git": {
                "get_status": "On branch main\nYour branch is up to date"
            }
        }
        
        # Chat with MCP context
        response = integration.agent.chat(
            message=message,
            external_context={"mcp_servers": mcp_context}
        )
        
        print(f"🤖 Gemini with MCP context: {response}")
        
    except Exception as e:
        print(f"❌ Error in MCP client example: {str(e)}")


async def example_bidirectional_mcp():
    """Example: Gemini as both MCP Server and Client"""
    print("\n🔄 Bidirectional MCP Example")
    print("=" * 50)
    
    # Create integration
    integration = GeminiMCPIntegration()
    
    # Create some conversation sessions
    integration.agent.create_session("project_planning", context_window=15)
    integration.agent.create_session("code_review", context_window=20)
    
    # Add some conversation history
    integration.agent.switch_session("project_planning")
    integration.agent.chat("I need to plan a Python web API project")
    integration.agent.chat("It should handle user authentication and data management")
    
    integration.agent.switch_session("code_review") 
    integration.agent.chat("Please review this Python function for best practices")
    integration.agent.chat("Focus on error handling and performance")
    
    # Now Gemini acts as MCP Server - other clients can query its sessions
    print("📤 As MCP Server - exposing Gemini capabilities:")
    sessions = integration.agent.list_sessions()
    print(f"   Sessions available to MCP clients: {list(sessions.keys())}")
    
    # Summary of conversations (available via MCP)
    summary = integration.agent.create_contextual_summary(["project_planning", "code_review"])
    print(f"   Contextual summary (via MCP): {summary[:200]}...")
    
    # Gemini acts as MCP Client - using external tools/resources
    print("\n📥 As MCP Client - using external MCP servers:")
    
    # Simulate calling external MCP tools
    external_context = {
        "code_analysis": {
            "pylint_check": "Score: 8.5/10 - Minor style issues",
            "security_scan": "No security vulnerabilities found"
        },
        "project_tools": {
            "github_status": "15 open issues, 3 pull requests",
            "ci_status": "All builds passing"
        }
    }
    
    # Use both internal context and external MCP data
    response = integration.agent.chat(
        message="Based on our project planning and code review discussions, plus the latest project status, what should be our next priorities?",
        context_sources=["project_planning", "code_review"],
        external_context=external_context
    )
    
    print(f"🎯 Integrated response: {response}")
    
    # Show final integration stats
    print(f"\n📊 Final Integration Stats:")
    stats = integration.get_integration_stats()
    print(f"   Total interactions: {stats['agent_stats']['total_interactions']}")
    print(f"   Active sessions: {len(stats['agent_stats']['session_stats'])}")


async def example_mcp_server_deployment():
    """Example: Deploying Gemini as MCP Server"""
    print("\n🚀 MCP Server Deployment Example")
    print("=" * 50)
    
    # Create integration
    integration = GeminiMCPIntegration()
    
    # Create server configuration
    config = create_mcp_server_config(host="127.0.0.1", port=3000, path="/gemini-mcp")
    
    print("⚙️  Server Configuration:")
    print(json.dumps(config, indent=2))
    
    # Save configuration
    with open("gemini_mcp_server_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved to gemini_mcp_server_config.json")
    print("\n🔧 To run the server:")
    print("   python -c \"from gemini_mcp_integration import *; import asyncio; asyncio.run(run_mcp_server(GeminiMCPIntegration()))\"")
    print("\n🔗 MCP clients can connect to:")
    print("   URL: http://127.0.0.1:3000/gemini-mcp")
    print("   Protocol: Model Context Protocol over HTTP")
    
    # Show what clients can access
    print("\n📋 What MCP clients will have access to:")
    print("   Tools: All Gemini AI capabilities (chat, image gen/analysis, document processing)")
    print("   Resources: Agent stats, session contexts, model information")
    print("   Sessions: Multi-context conversation management")


async def example_integration_patterns():
    """Example: Advanced MCP Integration Patterns"""
    print("\n🎨 Advanced Integration Patterns")
    print("=" * 50)
    
    integration = GeminiMCPIntegration()
    
    # Pattern 1: Session-based MCP routing
    print("1️⃣  Session-based MCP Routing:")
    
    # Create specialized sessions for different MCP integrations
    integration.agent.create_session("mcp_filesystem", context_window=10)
    integration.agent.create_session("mcp_database", context_window=15)
    integration.agent.create_session("mcp_apis", context_window=8)
    
    # Each session can be associated with specific MCP servers
    session_mcp_mapping = {
        "mcp_filesystem": ["filesystem", "git"],
        "mcp_database": ["postgres", "mongodb"],
        "mcp_apis": ["web_search", "weather", "news"]
    }
    
    print(f"   Session-MCP mapping: {session_mcp_mapping}")
    
    # Pattern 2: Context enrichment pipeline
    print("\n2️⃣  Context Enrichment Pipeline:")
    
    # Simulate a multi-step enrichment process
    steps = [
        "1. User input → Gemini analysis",
        "2. MCP tool calls for additional data",
        "3. Context merging from multiple sources", 
        "4. Final response generation",
        "5. Response caching in session"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    # Pattern 3: Fallback chain
    print("\n3️⃣  MCP Fallback Chain:")
    
    fallback_chain = {
        "primary": "high_performance_mcp_server",
        "secondary": "standard_mcp_server", 
        "tertiary": "local_fallback",
        "final": "gemini_only"
    }
    
    print(f"   Fallback chain: {fallback_chain}")
    
    # Pattern 4: Load balancing
    print("\n4️⃣  MCP Load Balancing:")
    
    load_balance_config = {
        "strategy": "round_robin",
        "servers": ["mcp_server_1", "mcp_server_2", "mcp_server_3"],
        "health_check": True,
        "retry_failed": 3
    }
    
    print(f"   Load balance config: {load_balance_config}")
    
    print("\n✨ These patterns enable:")
    benefits = [
        "Scalable MCP integrations",
        "Fault-tolerant operations", 
        "Context-aware routing",
        "Performance optimization",
        "Multi-source data fusion"
    ]
    
    for benefit in benefits:
        print(f"   • {benefit}")


async def interactive_mcp_demo():
    """Interactive demo of MCP integration"""
    print("\n🎮 Interactive MCP Demo")
    print("=" * 50)
    
    integration = GeminiMCPIntegration()
    
    print("Available commands:")
    print("  1. server-stats  - Show MCP server statistics")
    print("  2. client-tools  - Show available MCP client tools")
    print("  3. chat-mcp     - Chat with MCP context")
    print("  4. session-demo - Demonstrate session management")
    print("  5. quit         - Exit demo")
    
    while True:
        try:
            choice = input("\n👤 Enter command (1-5): ").strip()
            
            if choice == "1" or choice == "server-stats":
                stats = integration.get_integration_stats()
                print("📊 MCP Server Stats:")
                print(json.dumps(stats["agent_stats"], indent=2))
                
            elif choice == "2" or choice == "client-tools":
                tools = integration.client.list_available_tools()
                print("🛠️  Available MCP Tools:")
                if tools:
                    for server, tool_list in tools.items():
                        print(f"   {server}: {tool_list}")
                else:
                    print("   No MCP servers connected")
                    
            elif choice == "3" or choice == "chat-mcp":
                message = input("Enter your message: ")
                
                # Simulate MCP context
                mcp_context = {
                    "example_server": {
                        "current_time": "2024-07-24 14:30:00",
                        "system_status": "All systems operational"
                    }
                }
                
                response = integration.agent.chat(
                    message=message,
                    external_context={"mcp_context": mcp_context}
                )
                print(f"🤖 Gemini (with MCP): {response}")
                
            elif choice == "4" or choice == "session-demo":
                # Create and demonstrate sessions
                session_name = input("Enter session name: ")
                integration.agent.create_session(session_name)
                integration.agent.switch_session(session_name)
                
                message = input("Enter message for this session: ")
                response = integration.agent.chat(message)
                
                print(f"📝 Session '{session_name}' response: {response}")
                
                # Show session context
                context = integration.agent.get_session_context(session_name)
                print(f"🔍 Session context: {context}")
                
            elif choice == "5" or choice == "quit":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def main():
    """Run all MCP integration examples"""
    print("🤖 Gemini AI Agent - MCP Integration Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_mcp_server()
        await example_mcp_client()
        await example_bidirectional_mcp()
        await example_mcp_server_deployment()
        await example_integration_patterns()
        
        # Interactive demo
        await interactive_mcp_demo()
        
    except Exception as e:
        logger.error(f"Error in examples: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
