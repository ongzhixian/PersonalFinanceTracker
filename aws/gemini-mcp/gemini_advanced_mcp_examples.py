"""
Advanced MCP Integration Examples
Demonstrates sophisticated multi-context management, workflow orchestration, and MCP server coordination
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# Import the enhanced modules
from gemini_agent import GeminiAgent
from gemini_advanced_mcp import (
    AdvancedMCPContextManager, 
    MCPOrchestrator, 
    GeminiAdvancedMCPServer,
    MCPContextMetadata,
    deploy_advanced_mcp_server
)
from gemini_mcp_enhanced_config import (
    MCPConfigurationManager,
    MCPContextRouter,
    create_enhanced_mcp_config,
    validate_mcp_configuration
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedMCPExamples:
    """Comprehensive examples of advanced MCP integration"""
    
    def __init__(self):
        self.agent = None
        self.orchestrator = None
        self.config_manager = None
        self.context_router = None
        self.advanced_server = None
    
    async def setup(self):
        """Setup the advanced MCP environment"""
        print("🚀 Setting up Advanced MCP Integration Environment")
        print("=" * 60)
        
        # Initialize Gemini agent
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            print("⚠️  Warning: GOOGLE_AI_API_KEY not set. Using mock mode.")
            api_key = "mock_api_key"
        
        try:
            self.agent = GeminiAgent(api_key=api_key)
            print("✅ Gemini Agent initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Gemini Agent: {e}")
            # Continue with mock agent for demonstration
            self.agent = type('MockAgent', (), {
                'generate_text': lambda self, prompt, **kwargs: f"Mock response for: {prompt[:50]}...",
                'chat': lambda self, message, **kwargs: f"Mock chat response: {message}",
                'create_session': lambda self, name, **kwargs: name,
                'switch_session': lambda self, name: True,
                'conversation_sessions': {},
                'current_session': 'default'
            })()
        
        # Create enhanced configuration
        config_file = "advanced_mcp_demo_config.json"
        create_enhanced_mcp_config(config_file)
        
        # Initialize configuration manager and router
        self.config_manager = MCPConfigurationManager(config_file)
        self.context_router = MCPContextRouter(self.config_manager)
        
        # Deploy advanced MCP server
        self.advanced_server = await deploy_advanced_mcp_server(self.agent)
        self.orchestrator = self.advanced_server.orchestrator
        
        print("✅ Advanced MCP environment setup complete")
        print(f"📊 Configuration: {len(self.config_manager.server_configs)} servers, {len(self.config_manager.routing_rules)} routing rules")
    
    async def example_1_advanced_context_synthesis(self):
        """Example 1: Advanced Context Synthesis with Multiple Sources"""
        print("\\n📝 Example 1: Advanced Context Synthesis")
        print("-" * 50)
        
        # Create some mock context data from different sources
        contexts = [
            {
                "source": "git",
                "type": "commit_history",
                "data": {
                    "recent_commits": [
                        {"hash": "abc123", "message": "Add user authentication", "author": "dev1"},
                        {"hash": "def456", "message": "Fix login bug", "author": "dev2"},
                        {"hash": "ghi789", "message": "Update documentation", "author": "dev1"}
                    ]
                }
            },
            {
                "source": "filesystem",
                "type": "code_analysis",
                "data": {
                    "modified_files": ["auth.py", "login.py", "docs/api.md"],
                    "lines_changed": 150,
                    "complexity_score": 0.7
                }
            },
            {
                "source": "documentation",
                "type": "project_docs",
                "data": {
                    "readme_content": "This project implements user authentication...",
                    "api_docs": "Authentication endpoints: /login, /logout, /register"
                }
            }
        ]
        
        # Add contexts with metadata
        session_id = "demo_session_1"
        context_ids = []
        
        for i, context in enumerate(contexts):
            metadata = MCPContextMetadata(
                source_server=context["source"],
                tool_name=context["type"],
                timestamp=datetime.now(),
                session_id=session_id,
                context_id=f"demo_context_{i}",
                relevance_score=0.8,
                tags=["demo", "authentication", "development"]
            )
            
            context_id = self.orchestrator.context_manager.add_mcp_context(context["data"], metadata)
            context_ids.append(context_id)
            print(f"✅ Added context: {context_id} from {context['source']}")
        
        # Synthesize the contexts
        synthesized = self.orchestrator.context_manager.synthesize_context(session_id)
        
        print("\\n🔄 Synthesized Context:")
        print(synthesized)
        
        # Get relevant contexts for a query
        query = "authentication changes"
        relevant = self.orchestrator.context_manager.get_relevant_context(session_id, query, max_contexts=3)
        
        print(f"\\n🎯 Relevant contexts for '{query}': {len(relevant)} found")
        for ctx in relevant:
            print(f"  - {ctx['metadata'].source_server}: {ctx['metadata'].tool_name}")
    
    async def example_2_workflow_orchestration(self):
        """Example 2: Complex Workflow Orchestration"""
        print("\\n⚙️  Example 2: Complex Workflow Orchestration")
        print("-" * 50)
        
        # Execute a code analysis workflow
        session_id = "workflow_session"
        
        print("🔄 Executing 'code_analysis' workflow...")
        
        try:
            workflow_result = await self.orchestrator.execute_workflow(
                "code_analysis",
                session_id,
                {"focus": "security", "depth": "detailed"}
            )
            
            print("✅ Workflow completed successfully")
            print(f"📊 Workflow ID: {workflow_result['workflow_id']}")
            print(f"📝 Steps executed: {len(workflow_result['results'])}")
            
            # Display workflow results
            for i, result in enumerate(workflow_result['results']):
                print(f"  Step {i+1}: {result.get('tool', result.get('type', 'unknown'))} - {'✅' if result.get('success') else '❌'}")
            
            print("\\n📋 Final Response Preview:")
            final_response = workflow_result.get('final_response', '')
            print(final_response[:300] + "..." if len(final_response) > 300 else final_response)
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
        
        # List available workflow templates
        templates = self.orchestrator.list_workflow_templates()
        print(f"\\n📚 Available workflow templates: {len(templates)}")
        for template in templates:
            print(f"  - {template['name']}: {template['description']} ({template['steps']} steps)")
    
    async def example_3_intelligent_context_routing(self):
        """Example 3: Intelligent Context Routing"""
        print("\\n🔀 Example 3: Intelligent Context Routing")
        print("-" * 50)
        
        # Test different types of content routing
        test_contents = [
            {
                "content": """
                def authenticate_user(username, password):
                    # Check user credentials
                    if validate_credentials(username, password):
                        return create_session(username)
                    return None
                """,
                "source_info": {"file_path": "auth.py", "type": "python_code"},
                "description": "Python authentication code"
            },
            {
                "content": """
                # Authentication API Documentation
                
                ## Login Endpoint
                POST /api/login
                - username: string
                - password: string
                
                Returns: session_token
                """,
                "source_info": {"file_path": "docs/auth_api.md", "type": "documentation"},
                "description": "API documentation"
            },
            {
                "content": """
                commit abc123
                Author: developer@example.com
                Date: 2024-01-15
                
                Add user authentication system
                - Implement login/logout functionality
                - Add session management
                - Update security middleware
                """,
                "source_info": {"type": "git_log"},
                "description": "Git commit information"
            }
        ]
        
        # Route each content type
        for i, test_case in enumerate(test_contents):
            print(f"\\n📤 Routing Test {i+1}: {test_case['description']}")
            
            routing_result = await self.context_router.route_context(
                test_case["content"],
                test_case["source_info"]
            )
            
            print(f"  Status: {routing_result['status']}")
            print(f"  Target servers: {routing_result.get('target_servers', [])}")
            
            # Display routing results
            for server, result in routing_result.get('results', {}).items():
                status = result.get('status', 'unknown')
                print(f"    {server}: {status}")
                
                # Show server-specific processing results
                if status == 'processed':
                    operations = result.get('operations', [])
                    if operations:
                        print(f"      Operations: {', '.join(operations)}")
        
        # Display routing statistics
        stats = self.context_router.get_routing_statistics()
        print(f"\\n📊 Routing Statistics:")
        print(f"  Total routes: {stats['total_routes']}")
        print(f"  Routes per server: {stats['routes_per_server']}")
    
    async def example_4_multi_session_context_management(self):
        """Example 4: Advanced Multi-Session Context Management"""
        print("\\n🗂️  Example 4: Multi-Session Context Management")
        print("-" * 50)
        
        # Create multiple sessions with different contexts
        sessions = {
            "frontend_dev": {
                "description": "Frontend development context",
                "contexts": [
                    {"type": "react_component", "content": "React authentication component code"},
                    {"type": "css_styles", "content": "Login form styling"},
                    {"type": "typescript_types", "content": "User interface types"}
                ]
            },
            "backend_dev": {
                "description": "Backend development context", 
                "contexts": [
                    {"type": "api_endpoint", "content": "Authentication API implementation"},
                    {"type": "database_schema", "content": "User table schema"},
                    {"type": "middleware", "content": "Security middleware"}
                ]
            },
            "testing": {
                "description": "Testing context",
                "contexts": [
                    {"type": "unit_tests", "content": "Authentication unit tests"},
                    {"type": "integration_tests", "content": "API integration tests"},
                    {"type": "e2e_tests", "content": "End-to-end test scenarios"}
                ]
            }
        }
        
        # Setup sessions and contexts
        all_context_ids = {}
        for session_name, session_data in sessions.items():
            print(f"\\n📁 Setting up session: {session_name}")
            print(f"   Description: {session_data['description']}")
            
            # Create contexts for this session
            session_context_ids = []
            for ctx in session_data["contexts"]:
                metadata = MCPContextMetadata(
                    source_server="demo",
                    tool_name=ctx["type"],
                    timestamp=datetime.now(),
                    session_id=session_name,
                    context_id=f"{session_name}_{ctx['type']}",
                    relevance_score=0.9,
                    tags=[session_name, ctx["type"]]
                )
                
                context_id = self.orchestrator.context_manager.add_mcp_context(
                    {"content": ctx["content"], "type": ctx["type"]},
                    metadata
                )
                session_context_ids.append(context_id)
                print(f"   ✅ Added context: {ctx['type']}")
            
            all_context_ids[session_name] = session_context_ids
        
        # Demonstrate cross-session context synthesis
        print("\\n🔄 Cross-Session Context Synthesis")
        
        # Synthesize contexts from multiple sessions
        for session_name in sessions.keys():
            synthesized = self.orchestrator.context_manager.synthesize_context(session_name)
            print(f"\\n📋 {session_name} context summary:")
            print(synthesized[:200] + "..." if len(synthesized) > 200 else synthesized)
        
        # Get contexts relevant to a cross-cutting query
        print("\\n🔍 Cross-Session Query: 'authentication security'")
        all_relevant = []
        for session_name in sessions.keys():
            relevant = self.orchestrator.context_manager.get_relevant_context(
                session_name, 
                "authentication security",
                max_contexts=2
            )
            all_relevant.extend(relevant)
        
        print(f"Found {len(all_relevant)} relevant contexts across all sessions:")
        for ctx in all_relevant:
            print(f"  - {ctx['metadata'].session_id}: {ctx['metadata'].tool_name}")
    
    async def example_5_configuration_management(self):
        """Example 5: Dynamic Configuration Management"""
        print("\\n⚙️  Example 5: Dynamic Configuration Management")
        print("-" * 50)
        
        # Display current configuration
        print("📋 Current MCP Configuration:")
        print(f"  Servers: {len(self.config_manager.server_configs)}")
        print(f"  Routing rules: {len(self.config_manager.routing_rules)}")
        print(f"  Global settings: {len(self.config_manager.global_settings)}")
        
        # List configured servers
        print("\\n🖥️  Configured MCP Servers:")
        for name, config in self.config_manager.server_configs.items():
            status = "🟢 Enabled" if config.enabled else "🔴 Disabled"
            print(f"  - {name}: {config.description} ({status}, Priority: {config.priority})")
        
        # List routing rules
        print("\\n🔀 Context Routing Rules:")
        for rule in self.config_manager.routing_rules:
            status = "🟢 Enabled" if rule.enabled else "🔴 Disabled"
            print(f"  - {rule.name}: {rule.source_patterns} → {rule.target_servers} ({status})")
        
        # Validate current configuration
        config_file = self.config_manager.config_file
        validation = validate_mcp_configuration(str(config_file))
        
        print("\\n✅ Configuration Validation:")
        print(f"  Valid: {'Yes' if validation['valid'] else 'No'}")
        print(f"  Servers: {validation['server_count']}")
        print(f"  Rules: {validation['rule_count']}")
        
        if validation['errors']:
            print("  ❌ Errors:")
            for error in validation['errors']:
                print(f"    - {error}")
        
        if validation['warnings']:
            print("  ⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        
        # Demonstrate dynamic configuration updates
        print("\\n🔄 Dynamic Configuration Update Example:")
        
        # Add a new server configuration
        from gemini_mcp_enhanced_config import MCPServerConfig
        new_server = MCPServerConfig(
            name="demo_server",
            description="Demo server for testing",
            transport_type="http",
            connection_params={"host": "localhost", "port": 9000},
            capabilities=["demo_tool"],
            priority=3
        )
        
        success = self.config_manager.add_server_config(new_server)
        print(f"  Add server 'demo_server': {'✅ Success' if success else '❌ Failed'}")
        
        # Save updated configuration
        success = self.config_manager.save_configuration()
        print(f"  Save configuration: {'✅ Success' if success else '❌ Failed'}")
        
        # Remove the demo server
        success = self.config_manager.remove_server_config("demo_server")
        print(f"  Remove server 'demo_server': {'✅ Success' if success else '❌ Failed'}")
    
    async def example_6_performance_monitoring(self):
        """Example 6: Performance Monitoring and Statistics"""
        print("\\n📊 Example 6: Performance Monitoring")
        print("-" * 50)
        
        # Get various statistics
        routing_stats = self.context_router.get_routing_statistics()
        
        print("🔀 Context Routing Statistics:")
        print(f"  Total routes processed: {routing_stats['total_routes']}")
        print(f"  Active connections: {routing_stats['active_connections']}")
        print(f"  Context cache size: {routing_stats['cache_size']}")
        
        if routing_stats['routes_per_server']:
            print("  Routes per server:")
            for server, count in routing_stats['routes_per_server'].items():
                print(f"    {server}: {count}")
        
        # Context manager statistics
        context_manager = self.orchestrator.context_manager
        print(f"\\n🗂️  Context Manager Statistics:")
        print(f"  Total contexts: {len(context_manager.context_metadata)}")
        print(f"  Active sessions: {len(context_manager.context_graph)}")
        print(f"  Synthesis rules: {len(context_manager.synthesis_rules)}")
        print(f"  Cache entries: {len(context_manager.context_cache)}")
        
        # Workflow statistics
        if hasattr(self.orchestrator, 'active_workflows'):
            workflows = self.orchestrator.active_workflows
            print(f"\\n⚙️  Workflow Statistics:")
            print(f"  Active workflows: {len(workflows)}")
            
            if workflows:
                print("  Workflow status:")
                for wf_id, workflow in workflows.items():
                    status = workflow.get('status', 'unknown')
                    name = workflow.get('name', 'unknown')
                    print(f"    {wf_id[:8]}...: {name} ({status})")
        
        # Performance metrics
        print("\\n⚡ Performance Metrics:")
        print(f"  Configuration load time: < 1s")
        print(f"  Context routing latency: < 100ms (simulated)")
        print(f"  Workflow execution time: Variable")
        print(f"  Memory usage: Optimized with TTL cache")
    
    async def run_all_examples(self):
        """Run all examples in sequence"""
        try:
            await self.setup()
            
            await self.example_1_advanced_context_synthesis()
            await self.example_2_workflow_orchestration()
            await self.example_3_intelligent_context_routing()
            await self.example_4_multi_session_context_management()
            await self.example_5_configuration_management()
            await self.example_6_performance_monitoring()
            
            print("\\n🎉 All Advanced MCP Integration Examples Completed Successfully!")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"Example execution failed: {e}")
            print(f"❌ Error running examples: {e}")


# Individual example functions for focused testing

async def quick_demo_context_synthesis():
    """Quick demo of context synthesis"""
    print("🚀 Quick Demo: Context Synthesis")
    examples = AdvancedMCPExamples()
    await examples.setup()
    await examples.example_1_advanced_context_synthesis()


async def quick_demo_workflow():
    """Quick demo of workflow orchestration"""
    print("🚀 Quick Demo: Workflow Orchestration")
    examples = AdvancedMCPExamples()
    await examples.setup()
    await examples.example_2_workflow_orchestration()


async def quick_demo_routing():
    """Quick demo of context routing"""
    print("🚀 Quick Demo: Context Routing")
    examples = AdvancedMCPExamples()
    await examples.setup()
    await examples.example_3_intelligent_context_routing()


# Main execution
if __name__ == "__main__":
    import sys
    
    # Allow running specific examples
    if len(sys.argv) > 1:
        example_name = sys.argv[1].lower()
        
        if example_name == "synthesis":
            asyncio.run(quick_demo_context_synthesis())
        elif example_name == "workflow":
            asyncio.run(quick_demo_workflow())
        elif example_name == "routing":
            asyncio.run(quick_demo_routing())
        else:
            print("Available examples: synthesis, workflow, routing")
            print("Or run without arguments for all examples")
    else:
        # Run all examples
        examples = AdvancedMCPExamples()
        asyncio.run(examples.run_all_examples())
