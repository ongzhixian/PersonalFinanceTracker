"""
Advanced MCP Integration Features for Gemini AI Agent
Provides enhanced multi-context management, session orchestration, and advanced MCP patterns
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import uuid

try:
    from fastmcp import FastMCP, Context
    from mcp import ClientSession, StdioServerTransport
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
except ImportError as e:
    print(f"Missing MCP dependencies: {e}")
    print("Please install: pip install fastmcp mcp")
    exit(1)

from gemini_agent import GeminiAgent
from gemini_mcp_integration import GeminiMCPServer, GeminiMCPClient

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MCPContextMetadata:
    """Metadata for MCP context entries"""
    source_server: str
    tool_name: str
    timestamp: datetime
    session_id: str
    context_id: str
    relevance_score: float = 0.0
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ContextSynthesisRule:
    """Rules for synthesizing context from multiple sources"""
    name: str
    priority: int
    condition: Callable[[Dict[str, Any]], bool]
    synthesis_function: Callable[[List[Dict[str, Any]]], str]
    max_tokens: int = 1000


class AdvancedMCPContextManager:
    """Advanced context management with MCP integration"""
    
    def __init__(self, agent: GeminiAgent):
        self.agent = agent
        self.context_metadata: Dict[str, MCPContextMetadata] = {}
        self.context_graph: Dict[str, List[str]] = defaultdict(list)
        self.synthesis_rules: List[ContextSynthesisRule] = []
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl: timedelta = timedelta(minutes=10)
        
        # Initialize default synthesis rules
        self._setup_default_synthesis_rules()
    
    def _setup_default_synthesis_rules(self):
        """Setup default context synthesis rules"""
        
        # High priority: Recent code changes
        self.synthesis_rules.append(ContextSynthesisRule(
            name="recent_code_changes",
            priority=10,
            condition=lambda ctx: any("git" in k or "filesystem" in k for k in ctx.keys()),
            synthesis_function=self._synthesize_code_context,
            max_tokens=800
        ))
        
        # Medium priority: Documentation context
        self.synthesis_rules.append(ContextSynthesisRule(
            name="documentation",  
            priority=5,
            condition=lambda ctx: any("doc" in str(v).lower() or "readme" in str(v).lower() 
                                    for v in ctx.values()),
            synthesis_function=self._synthesize_doc_context,
            max_tokens=600
        ))
        
        # Low priority: General context
        self.synthesis_rules.append(ContextSynthesisRule(
            name="general",
            priority=1,
            condition=lambda ctx: True,
            synthesis_function=self._synthesize_general_context,
            max_tokens=400
        ))
    
    def _synthesize_code_context(self, contexts: List[Dict[str, Any]]) -> str:
        """Synthesize code-related context"""
        code_info = []
        for ctx in contexts:
            if "git" in str(ctx).lower():
                code_info.append(f"Git status: {ctx.get('content', '')[:200]}")
            elif "filesystem" in str(ctx).lower():
                code_info.append(f"File changes: {ctx.get('content', '')[:200]}")
        return "\n".join(code_info)
    
    def _synthesize_doc_context(self, contexts: List[Dict[str, Any]]) -> str:
        """Synthesize documentation context"""
        doc_info = []
        for ctx in contexts:
            content = ctx.get('content', '')
            if len(content) > 300:
                content = content[:300] + "..."
            doc_info.append(f"Documentation: {content}")
        return "\n".join(doc_info)
    
    def _synthesize_general_context(self, contexts: List[Dict[str, Any]]) -> str:
        """Synthesize general context"""
        general_info = []
        for ctx in contexts:
            content = str(ctx.get('content', ''))[:150]
            general_info.append(f"Context: {content}")
        return "\n".join(general_info)
    
    def add_mcp_context(self, 
                       context_data: Dict[str, Any], 
                       metadata: MCPContextMetadata) -> str:
        """Add MCP context with metadata"""
        context_id = str(uuid.uuid4())
        
        # Store context with metadata
        self.context_metadata[context_id] = metadata
        
        # Add to context graph for relationship tracking
        session_contexts = self.context_graph.get(metadata.session_id, [])
        session_contexts.append(context_id)
        self.context_graph[metadata.session_id] = session_contexts
        
        # Cache the context
        self.context_cache[context_id] = {
            'data': context_data,
            'metadata': metadata,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Added MCP context {context_id} from {metadata.source_server}")
        return context_id
    
    def get_relevant_context(self, 
                           session_id: str, 
                           query: str = None,
                           max_contexts: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context for a session/query"""
        session_contexts = self.context_graph.get(session_id, [])
        
        relevant_contexts = []
        for context_id in session_contexts:
            if context_id in self.context_cache:
                cache_entry = self.context_cache[context_id]
                
                # Check cache TTL
                if datetime.now() - cache_entry['timestamp'] > self.cache_ttl:
                    continue
                
                relevant_contexts.append(cache_entry)
        
        # Sort by relevance score and timestamp
        relevant_contexts.sort(
            key=lambda x: (x['metadata'].relevance_score, x['metadata'].timestamp),
            reverse=True
        )
        
        return relevant_contexts[:max_contexts]
    
    def synthesize_context(self, 
                         session_id: str, 
                         query: str = None) -> str:
        """Synthesize contextual information using rules"""
        relevant_contexts = self.get_relevant_context(session_id, query)
        
        if not relevant_contexts:
            return "No relevant context available."
        
        # Group contexts by applicable rules
        rule_contexts = defaultdict(list)
        for context in relevant_contexts:
            for rule in sorted(self.synthesis_rules, key=lambda x: x.priority, reverse=True):
                if rule.condition(context['data']):
                    rule_contexts[rule.name].append(context['data'])
                    break
        
        # Synthesize using rules
        synthesized_parts = []
        for rule_name, contexts in rule_contexts.items():
            rule = next(r for r in self.synthesis_rules if r.name == rule_name)
            synthesis = rule.synthesis_function(contexts)
            if synthesis:
                synthesized_parts.append(f"## {rule.name.replace('_', ' ').title()}\n{synthesis}")
        
        return "\n\n".join(synthesized_parts)


class MCPOrchestrator:
    """Orchestrates multiple MCP servers and manages complex workflows"""
    
    def __init__(self, agent: GeminiAgent):
        self.agent = agent
        self.context_manager = AdvancedMCPContextManager(agent)
        self.connected_servers: Dict[str, Any] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Setup default workflow templates
        self._setup_workflow_templates()
    
    def _setup_workflow_templates(self):
        """Setup default workflow templates"""
        
        # Code analysis workflow
        self.workflow_templates["code_analysis"] = {
            "name": "Code Analysis Workflow",
            "description": "Analyze code changes and provide insights",
            "steps": [
                {"tool": "git.get_status", "params": {}},
                {"tool": "git.get_diff", "params": {"files": "auto"}},
                {"tool": "filesystem.read_file", "params": {"path": "auto"}},
                {"synthesize": "code_context"},
                {"analyze": "code_quality_and_suggestions"}
            ],
            "context_synthesis": "recent_code_changes"
        }
        
        # Documentation workflow
        self.workflow_templates["documentation"] = {
            "name": "Documentation Generation",
            "description": "Generate documentation based on code and context",
            "steps": [
                {"tool": "filesystem.list_directory", "params": {"path": "."}},
                {"tool": "filesystem.read_file", "params": {"pattern": "*.md"}},
                {"synthesize": "doc_context"},
                {"generate": "documentation_update"}
            ],
            "context_synthesis": "documentation"
        }
        
        # Project overview workflow
        self.workflow_templates["project_overview"] = {
            "name": "Project Overview",
            "description": "Get comprehensive project overview",
            "steps": [
                {"tool": "git.get_log", "params": {"limit": 10}},
                {"tool": "filesystem.list_directory", "params": {"recursive": True}},
                {"tool": "filesystem.read_file", "params": {"path": "README.md"}},
                {"synthesize": "general_context"},
                {"analyze": "project_structure_and_status"}
            ],
            "context_synthesis": "general"
        }
    
    async def execute_workflow(self, 
                             workflow_name: str, 
                             session_id: str,
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name].copy()
        workflow_id = str(uuid.uuid4())
        
        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_name,
            "session_id": session_id,
            "status": "running",
            "started_at": datetime.now(),
            "steps": workflow["steps"],
            "results": [],
            "parameters": parameters or {}
        }
        
        logger.info(f"Starting workflow {workflow_name} (ID: {workflow_id})")
        
        try:
            results = []
            for i, step in enumerate(workflow["steps"]):
                step_result = await self._execute_workflow_step(step, workflow_id, session_id)
                results.append(step_result)
                
                # Add context if it's from an MCP tool
                if "tool" in step and step_result.get("success"):
                    metadata = MCPContextMetadata(
                        source_server=step["tool"].split(".")[0],
                        tool_name=step["tool"].split(".")[1],
                        timestamp=datetime.now(),
                        session_id=session_id,
                        context_id=f"{workflow_id}_step_{i}",
                        relevance_score=0.8,
                        tags=[workflow_name, "workflow"]
                    )
                    
                    self.context_manager.add_mcp_context(step_result, metadata)
            
            # Final synthesis
            synthesized_context = self.context_manager.synthesize_context(session_id)
            
            # Generate final response using Gemini
            final_prompt = f"""
            Based on the following workflow results and context, provide a comprehensive analysis:
            
            Workflow: {workflow['name']}
            Context: {synthesized_context}
            
            Please provide insights, recommendations, and actionable items.
            """
            
            final_response = await self._generate_workflow_response(final_prompt, session_id)
            
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
            self.active_workflows[workflow_id]["final_response"] = final_response
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "synthesized_context": synthesized_context,
                "final_response": final_response
            }
            
        except Exception as e:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
    
    async def _execute_workflow_step(self, 
                                   step: Dict[str, Any], 
                                   workflow_id: str,
                                   session_id: str) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            if "tool" in step:
                # Execute MCP tool (simulated for this example)
                tool_name = step["tool"]
                params = step.get("params", {})
                
                # In a real implementation, this would call the actual MCP tool
                result = {
                    "success": True,
                    "tool": tool_name,
                    "content": f"Simulated result for {tool_name} with params {params}",
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Executed tool {tool_name} in workflow {workflow_id}")
                return result
                
            elif "synthesize" in step:
                # Synthesize context
                synthesis_type = step["synthesize"]
                synthesized = self.context_manager.synthesize_context(session_id)
                
                return {
                    "success": True,
                    "type": "synthesis",
                    "synthesis_type": synthesis_type,
                    "content": synthesized,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif "analyze" in step or "generate" in step:
                # Use Gemini for analysis/generation
                task = step.get("analyze") or step.get("generate")
                context = self.context_manager.synthesize_context(session_id)
                
                prompt = f"Task: {task}\nContext: {context}\nPlease provide a detailed response."
                response = await self._generate_workflow_response(prompt, session_id)
                
                return {
                    "success": True,
                    "type": "analysis" if "analyze" in step else "generation",
                    "task": task,
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_workflow_response(self, prompt: str, session_id: str) -> str:
        """Generate response using Gemini for workflow steps"""
        # Use the agent to generate a response
        # In a real implementation, you might want to use a specific session
        return self.agent.generate_text(prompt, temperature=0.7, max_tokens=1024)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a running workflow"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        return {
            "id": workflow_id,
            "name": workflow["name"],
            "status": workflow["status"],
            "started_at": workflow["started_at"].isoformat(),
            "completed_at": workflow.get("completed_at", {}).isoformat() if workflow.get("completed_at") else None,
            "steps_completed": len(workflow.get("results", [])),
            "total_steps": len(workflow["steps"])
        }
    
    def list_workflow_templates(self) -> List[Dict[str, Any]]:
        """List available workflow templates"""
        return [
            {
                "name": name,
                "description": template["description"],
                "steps": len(template["steps"])
            }
            for name, template in self.workflow_templates.items()
        ]


class GeminiAdvancedMCPServer(GeminiMCPServer):
    """Enhanced MCP Server with advanced context management and workflows"""
    
    def __init__(self, agent: GeminiAgent, server_name: str = "GeminiAdvancedMCPServer"):
        super().__init__(agent, server_name)
        self.orchestrator = MCPOrchestrator(agent)
        self._setup_advanced_tools()
    
    def _setup_advanced_tools(self):
        """Setup advanced MCP tools"""
        
        @self.mcp.tool()
        def execute_workflow(workflow_name: str, 
                           session_id: str = None,
                           parameters: Optional[Dict[str, Any]] = None) -> str:
            """
            Execute a predefined workflow
            
            Args:
                workflow_name: Name of workflow to execute
                session_id: Session to use for context
                parameters: Workflow parameters
            """
            try:
                session_id = session_id or "default"
                result = asyncio.run(
                    self.orchestrator.execute_workflow(workflow_name, session_id, parameters)
                )
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error executing workflow: {str(e)}"
        
        @self.mcp.tool()
        def get_workflow_status(workflow_id: str) -> str:
            """
            Get status of a running workflow
            
            Args:
                workflow_id: ID of workflow to check
            """
            try:
                status = self.orchestrator.get_workflow_status(workflow_id)
                return json.dumps(status, indent=2)
            except Exception as e:
                return f"Error getting workflow status: {str(e)}"
        
        @self.mcp.tool()
        def list_workflow_templates() -> str:
            """List available workflow templates"""
            try:
                templates = self.orchestrator.list_workflow_templates()
                return json.dumps(templates, indent=2)
            except Exception as e:
                return f"Error listing templates: {str(e)}"
        
        @self.mcp.tool()
        def synthesize_context(session_id: str, query: Optional[str] = None) -> str:
            """
            Synthesize context from multiple MCP sources
            
            Args:
                session_id: Session to synthesize context for
                query: Optional query to focus synthesis
            """
            try:
                context = self.orchestrator.context_manager.synthesize_context(session_id, query)
                return context
            except Exception as e:
                return f"Error synthesizing context: {str(e)}"
        
        @self.mcp.tool()
        def add_context_synthesis_rule(name: str,
                                     priority: int,
                                     condition_description: str,
                                     max_tokens: int = 500) -> str:
            """
            Add a custom context synthesis rule
            
            Args:
                name: Name of the rule
                priority: Priority level (higher = more important)
                condition_description: Description of when to apply rule
                max_tokens: Maximum tokens for synthesis
            """
            try:
                # This is a simplified version - in practice you'd want more sophisticated rule creation
                def simple_condition(ctx):
                    return condition_description.lower() in str(ctx).lower()
                
                def simple_synthesis(contexts):
                    return f"Custom synthesis for {name}: " + "\n".join(str(ctx)[:100] for ctx in contexts)
                
                rule = ContextSynthesisRule(
                    name=name,
                    priority=priority,
                    condition=simple_condition,
                    synthesis_function=simple_synthesis,
                    max_tokens=max_tokens
                )
                
                self.orchestrator.context_manager.synthesis_rules.append(rule)
                return f"Added synthesis rule '{name}' with priority {priority}"
            except Exception as e:
                return f"Error adding synthesis rule: {str(e)}"


# Utility functions for configuration and deployment

def create_advanced_mcp_config(
    server_name: str = "GeminiAdvancedMCPServer",
    port: int = 8000,
    workflow_templates: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create configuration for advanced MCP server"""
    
    config = {
        "server": {
            "name": server_name,
            "version": "1.0.0",
            "description": "Advanced Gemini AI MCP Server with workflow orchestration"
        },
        "transport": {
            "type": "http",
            "host": "127.0.0.1",
            "port": port,
            "path": "/mcp"
        },
        "features": {
            "context_synthesis": True,
            "workflow_orchestration": True,
            "advanced_session_management": True,
            "multi_server_integration": True
        },
        "context_management": {
            "cache_ttl_minutes": 10,
            "max_contexts_per_session": 50,
            "default_synthesis_rules": ["recent_code_changes", "documentation", "general"]
        },
        "workflows": workflow_templates or {}
    }
    
    return config


async def deploy_advanced_mcp_server(
    agent: GeminiAgent,
    config: Dict[str, Any] = None,
    custom_workflows: Dict[str, Any] = None
) -> GeminiAdvancedMCPServer:
    """Deploy the advanced MCP server"""
    
    if not config:
        config = create_advanced_mcp_config()
    
    # Create server
    server = GeminiAdvancedMCPServer(agent, config["server"]["name"])
    
    # Add custom workflows if provided
    if custom_workflows:
        server.orchestrator.workflow_templates.update(custom_workflows)
    
    logger.info(f"Advanced MCP Server '{config['server']['name']}' deployed")
    logger.info(f"Available workflows: {list(server.orchestrator.workflow_templates.keys())}")
    
    return server


# Example usage
if __name__ == "__main__":
    import os
    
    # Example of deploying the advanced server
    async def main():
        # Initialize Gemini agent
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            print("Please set GOOGLE_AI_API_KEY environment variable")
            return
        
        agent = GeminiAgent(api_key=api_key)
        
        # Deploy advanced server
        server = await deploy_advanced_mcp_server(agent)
        
        # Example workflow execution
        workflow_result = await server.orchestrator.execute_workflow(
            "code_analysis",
            "example_session",
            {"focus": "security"}
        )
        
        print("Workflow Result:")
        print(json.dumps(workflow_result, indent=2))
    
    asyncio.run(main())
