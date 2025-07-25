"""
Enhanced MCP Configuration and Context Management System
Provides advanced configuration management, multi-server orchestration, and context routing
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    description: str
    transport_type: str  # stdio, sse, http
    connection_params: Dict[str, Any]
    capabilities: List[str]
    priority: int = 5
    enabled: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        return cls(**data)


@dataclass
class ContextRoutingRule:
    """Rules for routing context between MCP servers"""
    name: str
    source_patterns: List[str]  # Patterns to match source content
    target_servers: List[str]   # Target MCP servers
    transformation: Optional[str] = None  # Optional transformation function
    priority: int = 5
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MCPConfigurationManager:
    """Manages MCP server configurations and routing rules"""
    
    def __init__(self, config_file: str = "gemini_mcp_enhanced_config.json"):
        self.config_file = Path(config_file)
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.routing_rules: List[ContextRoutingRule] = []
        self.global_settings: Dict[str, Any] = {}
        
        # Load existing configuration
        self.load_configuration()
    
    def load_configuration(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    if self.config_file.suffix.lower() == '.yaml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Load server configurations
                for name, server_data in config_data.get('servers', {}).items():
                    self.server_configs[name] = MCPServerConfig.from_dict({
                        'name': name,
                        **server_data
                    })
                
                # Load routing rules
                for rule_data in config_data.get('routing_rules', []):
                    self.routing_rules.append(ContextRoutingRule(**rule_data))
                
                # Load global settings
                self.global_settings = config_data.get('global_settings', {})
                
                logger.info(f"Loaded configuration with {len(self.server_configs)} servers and {len(self.routing_rules)} routing rules")
                return True
            else:
                # Create default configuration
                self._create_default_configuration()
                return True
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'version': '1.0',
                'updated': datetime.now().isoformat(),
                'global_settings': self.global_settings,
                'servers': {
                    name: {k: v for k, v in config.to_dict().items() if k != 'name'}
                    for name, config in self.server_configs.items()
                },
                'routing_rules': [rule.to_dict() for rule in self.routing_rules]
            }
            
            with open(self.config_file, 'w') as f:
                if self.config_file.suffix.lower() == '.yaml':
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _create_default_configuration(self):
        """Create default configuration"""
        # Default global settings
        self.global_settings = {
            'max_concurrent_connections': 10,
            'default_timeout': 30,
            'context_cache_ttl_minutes': 15,
            'max_context_size_mb': 10,
            'enable_context_compression': True,
            'log_level': 'INFO'
        }
        
        # Default server configurations
        self.add_server_config(MCPServerConfig(
            name='filesystem',
            description='Local filesystem access',
            transport_type='stdio',
            connection_params={
                'command': 'npx',
                'args': ['@modelcontextprotocol/server-filesystem', '/tmp']
            },
            capabilities=['read_file', 'write_file', 'list_directory'],
            priority=8
        ))
        
        self.add_server_config(MCPServerConfig(
            name='git',
            description='Git repository operations',
            transport_type='stdio',
            connection_params={
                'command': 'npx',
                'args': ['@modelcontextprotocol/server-git']
            },
            capabilities=['get_status', 'get_log', 'get_diff'],
            priority=7
        ))
        
        # Add existing orchestrator server
        self.add_server_config(MCPServerConfig(
            name='orchestrator',
            description='Main orchestrator MCP server',
            transport_type='http',
            connection_params={
                'host': '127.0.0.1',
                'port': 14600,
                'path': '/mcp-server/mcp'
            },
            capabilities=['orchestrate', 'manage_workflows'],
            priority=9
        ))
        
        # Default routing rules
        self.add_routing_rule(ContextRoutingRule(
            name='code_to_git_and_filesystem',
            source_patterns=['*.py', '*.js', '*.ts', '*.java', '*.cpp'],
            target_servers=['git', 'filesystem'],
            priority=8
        ))
        
        self.add_routing_rule(ContextRoutingRule(
            name='documentation_to_filesystem',
            source_patterns=['*.md', '*.txt', '*.rst'],
            target_servers=['filesystem'],
            priority=6
        ))
        
        # Save the default configuration
        self.save_configuration()
    
    def add_server_config(self, config: MCPServerConfig) -> bool:
        """Add or update server configuration"""
        try:
            self.server_configs[config.name] = config
            logger.info(f"Added server configuration: {config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add server configuration: {e}")
            return False
    
    def remove_server_config(self, name: str) -> bool:
        """Remove server configuration"""
        if name in self.server_configs:
            del self.server_configs[name]
            logger.info(f"Removed server configuration: {name}")
            return True
        return False
    
    def add_routing_rule(self, rule: ContextRoutingRule) -> bool:
        """Add context routing rule"""
        try:
            self.routing_rules.append(rule)
            # Sort by priority
            self.routing_rules.sort(key=lambda x: x.priority, reverse=True)
            logger.info(f"Added routing rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add routing rule: {e}")
            return False
    
    def get_enabled_servers(self) -> List[MCPServerConfig]:
        """Get list of enabled server configurations"""
        return [config for config in self.server_configs.values() if config.enabled]
    
    def get_routing_rules_for_content(self, content: str, file_path: str = None) -> List[ContextRoutingRule]:
        """Get applicable routing rules for content"""
        applicable_rules = []
        
        for rule in self.routing_rules:
            if not rule.enabled:
                continue
            
            # Check patterns
            for pattern in rule.source_patterns:
                if file_path and self._matches_pattern(file_path, pattern):
                    applicable_rules.append(rule)
                    break
                elif pattern.lower() in content.lower():
                    applicable_rules.append(rule)
                    break
        
        return applicable_rules
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)


class MCPContextRouter:
    """Routes context between different MCP servers based on rules"""
    
    def __init__(self, config_manager: MCPConfigurationManager):
        self.config_manager = config_manager
        self.active_connections: Dict[str, Any] = {}
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        self.routing_stats: Dict[str, int] = defaultdict(int)
    
    async def route_context(self, 
                          content: str, 
                          source_info: Dict[str, Any] = None,
                          target_servers: List[str] = None) -> Dict[str, Any]:
        """Route context to appropriate MCP servers"""
        
        # Get applicable routing rules if no target servers specified
        if not target_servers:
            file_path = source_info.get('file_path') if source_info else None
            rules = self.config_manager.get_routing_rules_for_content(content, file_path)
            target_servers = []
            
            for rule in rules:
                target_servers.extend(rule.target_servers)
            
            # Remove duplicates while preserving order
            target_servers = list(dict.fromkeys(target_servers))
        
        if not target_servers:
            logger.warning("No target servers found for content routing")
            return {'status': 'no_targets', 'results': {}}
        
        # Route to each target server
        results = {}
        for server_name in target_servers:
            try:
                if server_name in self.config_manager.server_configs:
                    result = await self._route_to_server(server_name, content, source_info)
                    results[server_name] = result
                    self.routing_stats[server_name] += 1
                else:
                    logger.warning(f"Unknown server: {server_name}")
                    results[server_name] = {'status': 'unknown_server', 'error': f'Server {server_name} not configured'}
            
            except Exception as e:
                logger.error(f"Failed to route to server {server_name}: {e}")
                results[server_name] = {'status': 'error', 'error': str(e)}
        
        return {
            'status': 'completed',
            'target_servers': target_servers,
            'results': results,
            'routing_stats': dict(self.routing_stats)
        }
    
    async def _route_to_server(self, 
                             server_name: str, 
                             content: str, 
                             source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route content to a specific MCP server"""
        
        server_config = self.config_manager.server_configs[server_name]
        
        # This is a simplified implementation
        # In practice, you would establish actual MCP connections and call tools
        
        # Simulate server-specific processing
        if server_name == 'filesystem':
            return await self._process_filesystem_context(content, source_info)
        elif server_name == 'git':
            return await self._process_git_context(content, source_info)
        elif server_name == 'orchestrator':
            return await self._process_orchestrator_context(content, source_info)
        else:
            # Generic processing
            return {
                'status': 'processed',
                'server': server_name,
                'content_length': len(content),
                'processed_at': datetime.now().isoformat()
            }
    
    async def _process_filesystem_context(self, content: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content for filesystem server"""
        return {
            'status': 'processed',
            'server': 'filesystem',
            'operations': ['file_analysis', 'path_extraction'],
            'file_references': self._extract_file_references(content),
            'content_type': self._detect_content_type(content)
        }
    
    async def _process_git_context(self, content: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content for git server"""
        return {
            'status': 'processed',
            'server': 'git',
            'operations': ['commit_analysis', 'branch_detection'],
            'git_references': self._extract_git_references(content),
            'change_indicators': self._detect_changes(content)
        }
    
    async def _process_orchestrator_context(self, content: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content for orchestrator server"""
        return {
            'status': 'processed',
            'server': 'orchestrator',
            'operations': ['workflow_analysis', 'task_extraction'],
            'suggested_workflows': self._suggest_workflows(content),
            'complexity_score': self._calculate_complexity(content)
        }
    
    def _extract_file_references(self, content: str) -> List[str]:
        """Extract file references from content"""
        import re
        # Simple pattern for file paths
        file_pattern = r'[\w\-_./]+\.[a-zA-Z0-9]+'
        return list(set(re.findall(file_pattern, content)))
    
    def _detect_content_type(self, content: str) -> str:
        """Detect content type"""
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in ['def ', 'class ', 'import ', 'function']):
            return 'code'
        elif any(keyword in content_lower for keyword in ['# ', '## ', '### ', 'readme']):
            return 'documentation'
        elif any(keyword in content_lower for keyword in ['commit', 'merge', 'branch', 'git']):
            return 'git'
        else:
            return 'text'
    
    def _extract_git_references(self, content: str) -> List[str]:
        """Extract git-related references"""
        import re
        git_pattern = r'(commit|branch|merge|pull|push)\s+[\w\-/]+'
        return list(set(re.findall(git_pattern, content, re.IGNORECASE)))
    
    def _detect_changes(self, content: str) -> List[str]:
        """Detect change indicators in content"""
        change_indicators = []
        content_lower = content.lower()
        
        if 'added' in content_lower or 'new' in content_lower:
            change_indicators.append('addition')
        if 'removed' in content_lower or 'deleted' in content_lower:
            change_indicators.append('deletion')
        if 'modified' in content_lower or 'changed' in content_lower:
            change_indicators.append('modification')
        
        return change_indicators
    
    def _suggest_workflows(self, content: str) -> List[str]:
        """Suggest relevant workflows based on content"""
        workflows = []
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['code', 'function', 'class']):
            workflows.append('code_analysis')
        if any(keyword in content_lower for keyword in ['doc', 'readme', 'markdown']):
            workflows.append('documentation')
        if any(keyword in content_lower for keyword in ['test', 'spec', 'unit']):
            workflows.append('testing')
        if any(keyword in content_lower for keyword in ['deploy', 'build', 'ci']):
            workflows.append('deployment')
        
        return workflows
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score"""
        # Simple complexity calculation
        lines = content.split('\n')
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        unique_words = len(set(content.split()))
        
        complexity = min((avg_line_length / 50) + (unique_words / 100), 1.0)
        return round(complexity, 2)
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            'total_routes': sum(self.routing_stats.values()),
            'routes_per_server': dict(self.routing_stats),
            'active_connections': len(self.active_connections),
            'cache_size': len(self.context_cache)
        }


# Utility functions for enhanced configuration

def create_enhanced_mcp_config(output_file: str = "gemini_mcp_enhanced_config.json") -> bool:
    """Create an enhanced MCP configuration file"""
    try:
        config_manager = MCPConfigurationManager(output_file)
        # The default configuration is created automatically
        logger.info(f"Enhanced MCP configuration created: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create enhanced configuration: {e}")
        return False


def validate_mcp_configuration(config_file: str) -> Dict[str, Any]:
    """Validate MCP configuration file"""
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'server_count': 0,
        'rule_count': 0
    }
    
    try:
        config_manager = MCPConfigurationManager(config_file)
        validation_results['server_count'] = len(config_manager.server_configs)
        validation_results['rule_count'] = len(config_manager.routing_rules)
        
        # Validate server configurations
        for name, config in config_manager.server_configs.items():
            if not config.connection_params:
                validation_results['errors'].append(f"Server '{name}' missing connection parameters")
            
            if config.priority < 1 or config.priority > 10:
                validation_results['warnings'].append(f"Server '{name}' priority should be between 1-10")
        
        # Validate routing rules
        for rule in config_manager.routing_rules:
            if not rule.target_servers:
                validation_results['errors'].append(f"Routing rule '{rule.name}' has no target servers")
            
            # Check if target servers exist
            for server in rule.target_servers:
                if server not in config_manager.server_configs:
                    validation_results['warnings'].append(f"Routing rule '{rule.name}' references unknown server '{server}'")
        
        if validation_results['errors']:
            validation_results['valid'] = False
        
    except Exception as e:
        validation_results['valid'] = False
        validation_results['errors'].append(f"Configuration error: {str(e)}")
    
    return validation_results


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create enhanced configuration
        create_enhanced_mcp_config("test_enhanced_config.json")
        
        # Load and test configuration
        config_manager = MCPConfigurationManager("test_enhanced_config.json")
        router = MCPContextRouter(config_manager)
        
        # Test context routing
        test_content = """
        def analyze_code(file_path):
            # This function analyzes Python code
            with open(file_path, 'r') as f:
                content = f.read()
            return content
        """
        
        result = await router.route_context(
            test_content, 
            source_info={'file_path': 'analyzer.py'}
        )
        
        print("Routing Result:")
        print(json.dumps(result, indent=2))
        
        # Validate configuration
        validation = validate_mcp_configuration("test_enhanced_config.json")
        print("\\nValidation Result:")
        print(json.dumps(validation, indent=2))
    
    asyncio.run(main())
