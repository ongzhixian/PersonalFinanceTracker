# Advanced Gemini AI Agent MCP Integration

## Overview

This advanced MCP (Model Context Protocol) integration provides sophisticated multi-context management, workflow orchestration, and intelligent routing capabilities for the Gemini AI Agent. It extends the basic MCP functionality with enterprise-grade features for complex development workflows.

## 🌟 Key Features

### 1. Advanced Context Management
- **Multi-Source Context Synthesis**: Intelligently combines context from multiple MCP servers
- **Context Metadata Tracking**: Rich metadata for context provenance and relevance scoring
- **Smart Context Caching**: TTL-based caching with compression for performance
- **Cross-Session Context Sharing**: Share and merge contexts across different conversation sessions

### 2. Workflow Orchestration
- **Predefined Workflow Templates**: Ready-to-use workflows for common development tasks
- **Custom Workflow Creation**: Define your own multi-step workflows
- **Parallel/Sequential Execution**: Control workflow execution patterns
- **Error Handling & Retry Logic**: Robust error handling with automatic retries

### 3. Intelligent Context Routing
- **Pattern-Based Routing**: Route content based on file patterns and content types
- **Server Capability Matching**: Automatically route to servers with required capabilities
- **Priority-Based Processing**: Handle high-priority content first
- **Dynamic Rule Engine**: Add and modify routing rules at runtime

### 4. Enhanced Configuration Management
- **Hierarchical Configuration**: Organize settings by categories and priorities
- **Dynamic Updates**: Modify configuration without restarts
- **Validation & Testing**: Built-in configuration validation
- **Environment-Specific Settings**: Support for development, staging, and production configurations

##  Architecture

### Core Components

```
Gemini AI Agent
├── GeminiAdvancedMCPServer (MCP Server Interface)
├── AdvancedMCPContextManager (Context Management)
├── MCPOrchestrator (Workflow Management)
├── MCPConfigurationManager (Configuration)
└── MCPContextRouter (Intelligent Routing)
```

### Integration Flow

```
User Request → Context Router → Multiple MCP Servers → Context Synthesis → Gemini AI → Response
```

## 📦 Installation & Setup

### Prerequisites

```bash
pip install google-genai pillow fastmcp mcp pyyaml httpx
```

### Environment Variables

```bash
export GOOGLE_AI_API_KEY="your_gemini_api_key"
```

### Basic Setup

```python
from gemini_agent import GeminiAgent
from gemini_advanced_mcp import deploy_advanced_mcp_server
import asyncio

async def setup_advanced_mcp():
    # Initialize Gemini agent
    agent = GeminiAgent(api_key="your_api_key")
    
    # Deploy advanced MCP server
    server = await deploy_advanced_mcp_server(agent)
    
    print("Advanced MCP server deployed!")
    return server

# Run setup
server = asyncio.run(setup_advanced_mcp())
```

## 🔧 Configuration

### Configuration File Structure

The system uses JSON configuration files with the following structure:

```json
{
  "global_settings": {
    "max_concurrent_connections": 15,
    "context_cache_ttl_minutes": 20,
    "enable_smart_routing": true
  },
  "servers": {
    "server_name": {
      "description": "Server description",
      "transport_type": "stdio|http|sse",
      "connection_params": {...},
      "capabilities": [...],
      "priority": 1-10
    }
  },
  "routing_rules": [...],
  "workflows": {...}
}
```

### Server Configuration

#### Filesystem Server
```json
{
  "filesystem": {
    "description": "Enhanced filesystem operations",
    "transport_type": "stdio",
    "connection_params": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path"]
    },
    "capabilities": ["read_file", "write_file", "list_directory"],
    "priority": 8
  }
}
```

#### Git Server
```json
{
  "git": {
    "description": "Git repository operations",
    "transport_type": "stdio",
    "connection_params": {
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-git"]
    },
    "capabilities": ["get_status", "get_log", "get_diff"],
    "priority": 9
  }
}
```

### Routing Rules

```json
{
  "routing_rules": [
    {
      "name": "code_analysis_routing",
      "source_patterns": ["*.py", "*.js", "*.ts"],
      "target_servers": ["filesystem", "git", "gemini_agent"],
      "priority": 9,
      "enabled": true
    }
  ]
}
```

## 🔄 Workflow Management

### Predefined Workflows

#### Code Analysis Workflow
```python
workflow_result = await orchestrator.execute_workflow(
    "code_analysis",
    session_id="my_session",
    parameters={"focus": "security", "depth": "detailed"}
)
```

#### Documentation Generation Workflow
```python
workflow_result = await orchestrator.execute_workflow(
    "project_documentation_update", 
    session_id="docs_session"
)
```

### Custom Workflow Creation

```python
custom_workflow = {
    "name": "Custom Analysis",
    "description": "My custom workflow",
    "steps": [
        {"tool": "git.get_status", "params": {}},
        {"tool": "filesystem.read_file", "params": {"path": "README.md"}},
        {"synthesize": "doc_context"},
        {"analyze": "project_health"}
    ]
}

orchestrator.workflow_templates["custom_analysis"] = custom_workflow
```

## 🧠 Context Management

### Context Synthesis Rules

The system includes intelligent context synthesis with predefined rules:

- **Recent Code Changes**: Prioritizes recent commits and file modifications
- **Documentation**: Focuses on README files, comments, and documentation
- **Security**: Emphasizes security-related patterns and vulnerabilities
- **General**: Provides overall project context

### Adding Custom Context

```python
from gemini_advanced_mcp import MCPContextMetadata
from datetime import datetime

metadata = MCPContextMetadata(
    source_server="custom_server",
    tool_name="custom_analysis",
    timestamp=datetime.now(),
    session_id="my_session",
    context_id="unique_id",
    relevance_score=0.9,
    tags=["custom", "analysis"]
)

context_id = context_manager.add_mcp_context(
    {"analysis_result": "Custom analysis data"},
    metadata
)
```

### Context Synthesis

```python
# Synthesize context for a session
synthesized = context_manager.synthesize_context("my_session")

# Get relevant contexts for a query
relevant_contexts = context_manager.get_relevant_context(
    "my_session",
    query="security vulnerabilities",
    max_contexts=5
)
```

## 🔀 Context Routing

### Automatic Routing

The system automatically routes content based on:
- File extensions and patterns
- Content analysis
- Server capabilities
- Priority rules

```python
# Route content automatically
routing_result = await context_router.route_context(
    content="def authenticate_user(username, password):",
    source_info={"file_path": "auth.py", "type": "python_code"}
)
```

### Manual Routing

```python
# Route to specific servers
routing_result = await context_router.route_context(
    content="Project documentation content",
    target_servers=["filesystem", "gemini_agent"]
)
```

## 🛠️ Available MCP Tools

### Core Gemini Tools
- `generate_text(prompt, temperature, max_tokens, session_name)`
- `chat(message, session_name, maintain_context, context_sources)`
- `analyze_image(image_path, prompt)`
- `process_document(file_path, question)`

### Session Management Tools
- `create_session(session_name, context_window)`
- `switch_session(session_name)`
- `export_session(session_name, format_type)`

### Advanced Context Tools
- `merge_session_contexts(session_names, max_entries)`
- `create_contextual_summary(session_names, max_entries)`
- `synthesize_context(session_id, query)`

### Workflow Tools
- `execute_workflow(workflow_name, session_id, parameters)`
- `get_workflow_status(workflow_id)`
- `list_workflow_templates()`

## 📊 MCP Resources

### Available Resources
- `gemini://agent/stats` - Agent usage statistics
- `gemini://sessions/list` - List all conversation sessions
- `gemini://session/{session_name}/context` - Session context
- `gemini://models/available` - Available Gemini models

### Resource Access

```python
# Access resources via MCP protocol
stats = await mcp_client.read_resource("gemini://agent/stats")
sessions = await mcp_client.read_resource("gemini://sessions/list")
```

## 🔍 Monitoring & Performance

### Built-in Metrics
- Request/response times
- Error rates
- Context cache hit rates
- Workflow completion rates
- Memory usage

### Performance Optimization
- Context caching with TTL
- Intelligent routing to reduce server load
- Parallel workflow execution where possible
- Connection pooling for HTTP servers

### Monitoring Example

```python
# Get routing statistics
stats = context_router.get_routing_statistics()
print(f"Total routes: {stats['total_routes']}")
print(f"Cache hit rate: {stats['cache_hit_rate']}")

# Get workflow statistics
workflow_stats = orchestrator.get_workflow_statistics()
print(f"Active workflows: {len(workflow_stats['active'])}")
```

## 🚀 Example Use Cases

### 1. Code Review Automation

```python
async def automated_code_review():
    # Execute comprehensive code analysis
    result = await orchestrator.execute_workflow(
        "comprehensive_code_analysis",
        "code_review_session",
        {"focus": "security_and_performance"}
    )
    
    # Get AI-powered insights
    insights = result['final_response']
    return insights
```

### 2. Documentation Generation

```python
async def generate_project_docs():
    # Update documentation based on current project state
    result = await orchestrator.execute_workflow(
        "project_documentation_update",
        "docs_session"
    )
    
    return result['synthesized_context']
```

### 3. Multi-Context Analysis

```python
async def cross_session_analysis():
    # Create contexts from different sources
    frontend_context = "React component analysis..."
    backend_context = "API endpoint analysis..."
    
    # Route contexts to appropriate servers
    await context_router.route_context(frontend_context, {"type": "frontend"})
    await context_router.route_context(backend_context, {"type": "backend"})
    
    # Synthesize cross-cutting insights
    synthesis = context_manager.synthesize_context("analysis_session")
    return synthesis
```

## 🔐 Security & Best Practices

### Security Features
- Optional API key authentication
- Rate limiting
- Input validation
- Secure context isolation

### Best Practices
1. **Session Management**: Use descriptive session names and clean up old sessions
2. **Context Size**: Monitor context sizes to avoid memory issues
3. **Error Handling**: Always handle workflow failures gracefully
4. **Configuration**: Validate configuration changes before deployment
5. **Monitoring**: Monitor performance metrics and error rates

### Resource Management

```python
# Clean up old contexts
context_manager.cleanup_expired_contexts()

# Monitor memory usage
stats = context_manager.get_memory_usage()
if stats['memory_mb'] > 500:
    context_manager.compress_contexts()
```

## 🧪 Testing & Development

### Running Examples

```bash
# Run all examples
python gemini_advanced_mcp_examples.py

# Run specific examples
python gemini_advanced_mcp_examples.py synthesis
python gemini_advanced_mcp_examples.py workflow
python gemini_advanced_mcp_examples.py routing
```

### Configuration Validation

```python
from gemini_mcp_enhanced_config import validate_mcp_configuration

validation = validate_mcp_configuration("config.json")
if not validation['valid']:
    print("Configuration errors:", validation['errors'])
```

### Mock Mode

For testing without actual MCP servers:

```python
# Enable mock mode in configuration
{
  "development": {
    "mock_external_services": true,
    "simulate_network_delays": false
  }
}
```

## 📚 API Reference

### MCPOrchestrator Methods

```python
class MCPOrchestrator:
    async def execute_workflow(workflow_name, session_id, parameters=None)
    def get_workflow_status(workflow_id)
    def list_workflow_templates()
    def add_workflow_template(name, template)
```

### AdvancedMCPContextManager Methods

```python
class AdvancedMCPContextManager:
    def add_mcp_context(context_data, metadata)
    def get_relevant_context(session_id, query=None, max_contexts=5)
    def synthesize_context(session_id, query=None)
    def cleanup_expired_contexts()
```

### MCPContextRouter Methods

```python
class MCPContextRouter:
    async def route_context(content, source_info=None, target_servers=None)
    def get_routing_statistics()
    def add_routing_rule(rule)
```

## 🐛 Troubleshooting

### Common Issues

1. **Server Connection Failures**
   - Check server configurations and network connectivity
   - Verify MCP server is running and accessible
   - Review timeout settings

2. **Context Memory Issues**
   - Enable context compression
   - Reduce context TTL
   - Clean up old sessions regularly

3. **Workflow Failures**
   - Check workflow step dependencies
   - Verify server capabilities
   - Review error logs

4. **Performance Issues**
   - Enable caching
   - Optimize routing rules
   - Monitor server load

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Enable verbose configuration
{
  "development": {
    "debug_mode": true,
    "verbose_logging": true
  }
}
```

## 🤝 Contributing

To extend the advanced MCP integration:

1. **Adding New Servers**: Update configuration and add server-specific processors
2. **Custom Workflows**: Create workflow templates and add to configuration
3. **Synthesis Rules**: Implement custom context synthesis functions
4. **Routing Rules**: Add new routing patterns and conditions

## 📄 License

This advanced MCP integration follows the same license as the main Gemini AI Agent project.

---

For more information and updates, check the project repository and documentation.
