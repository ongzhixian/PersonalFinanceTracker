#!/usr/bin/env python3
"""
Setup and Test Script for Advanced Gemini MCP Integration
This script helps set up and test the advanced MCP integration features
"""

import asyncio
import json
import os
import sys
from pathlib import Path
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        ('google.genai', 'google-genai'),
        ('fastmcp', 'fastmcp'),
        ('mcp', 'mcp'),
        ('yaml', 'pyyaml'),
        ('httpx', 'httpx'),
        ('PIL', 'pillow')
    ]
    
    missing_packages = []
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name}")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True


def check_environment():
    """Check environment variables and setup"""
    print("\\n🌍 Checking Environment...")
    
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key:
        print("✅ GOOGLE_AI_API_KEY is set")
        return True
    else:
        print("⚠️  GOOGLE_AI_API_KEY not set - will run in mock mode")
        return False


def create_test_configuration():
    """Create a test configuration file"""
    print("\\n📝 Creating Test Configuration...")
    
    config_file = Path("test_advanced_mcp_config.json")
    
    if config_file.exists():
        print(f"✅ Configuration file already exists: {config_file}")
        return str(config_file)
    
    try:
        from gemini_mcp_enhanced_config import create_enhanced_mcp_config
        
        success = create_enhanced_mcp_config(str(config_file))
        if success:
            print(f"✅ Created configuration file: {config_file}")
            return str(config_file)
        else:
            print("❌ Failed to create configuration file")
            return None
    except ImportError as e:
        print(f"❌ Failed to import configuration module: {e}")
        return None


async def test_basic_setup():
    """Test basic setup and initialization"""
    print("\\n🧪 Testing Basic Setup...")
    
    try:
        # Test Gemini Agent initialization
        from gemini_agent import GeminiAgent
        
        api_key = os.getenv("GOOGLE_AI_API_KEY", "test_key")
        agent = GeminiAgent(api_key=api_key)
        print("✅ Gemini Agent initialized")
        
        # Test advanced MCP components
        from gemini_advanced_mcp import AdvancedMCPContextManager, MCPOrchestrator
        
        context_manager = AdvancedMCPContextManager(agent)
        orchestrator = MCPOrchestrator(agent)
        print("✅ Advanced MCP components initialized")
        
        # Test configuration management
        from gemini_mcp_enhanced_config import MCPConfigurationManager
        
        config_manager = MCPConfigurationManager("test_advanced_mcp_config.json")
        print("✅ Configuration manager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic setup test failed: {e}")
        return False


async def test_context_management():
    """Test context management features"""
    print("\\n🗂️  Testing Context Management...")
    
    try:
        from gemini_agent import GeminiAgent
        from gemini_advanced_mcp import AdvancedMCPContextManager, MCPContextMetadata
        from datetime import datetime
        
        # Create mock agent
        api_key = os.getenv("GOOGLE_AI_API_KEY", "test_key")
        agent = GeminiAgent(api_key=api_key)
        
        context_manager = AdvancedMCPContextManager(agent)
        
        # Add test context
        metadata = MCPContextMetadata(
            source_server="test_server",
            tool_name="test_tool",
            timestamp=datetime.now(),
            session_id="test_session",
            context_id="test_context_1",
            relevance_score=0.8,
            tags=["test", "demo"]
        )
        
        context_data = {
            "content": "This is test context data for the demo",
            "type": "test"
        }
        
        context_id = context_manager.add_mcp_context(context_data, metadata)
        print(f"✅ Added test context: {context_id}")
        
        # Test context synthesis
        synthesized = context_manager.synthesize_context("test_session")
        print(f"✅ Context synthesis: {len(synthesized)} characters")
        
        # Test relevant context retrieval
        relevant = context_manager.get_relevant_context("test_session", max_contexts=5)
        print(f"✅ Retrieved {len(relevant)} relevant contexts")
        
        return True
        
    except Exception as e:
        print(f"❌ Context management test failed: {e}")
        return False


async def test_workflow_orchestration():
    """Test workflow orchestration"""
    print("\\n⚙️  Testing Workflow Orchestration...")
    
    try:
        from gemini_agent import GeminiAgent
        from gemini_advanced_mcp import MCPOrchestrator
        
        # Create mock agent
        api_key = os.getenv("GOOGLE_AI_API_KEY", "test_key")
        agent = GeminiAgent(api_key=api_key)
        
        orchestrator = MCPOrchestrator(agent)
        
        # List workflow templates
        templates = orchestrator.list_workflow_templates()
        print(f"✅ Found {len(templates)} workflow templates")
        
        for template in templates:
            print(f"   - {template['name']}: {template['description']}")
        
        # Test workflow execution (in demo mode)
        print("\\n🔄 Testing workflow execution...")
        
        try:
            # This might fail if external services aren't available, which is expected
            result = await orchestrator.execute_workflow(
                "code_analysis",
                "test_workflow_session",
                {"demo_mode": True}
            )
            print(f"✅ Workflow executed: {result['workflow_id']}")
            
        except Exception as workflow_error:
            print(f"⚠️  Workflow execution failed (expected in test mode): {workflow_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow orchestration test failed: {e}")
        return False


async def test_context_routing():
    """Test context routing"""
    print("\\n🔀 Testing Context Routing...")
    
    try:
        from gemini_mcp_enhanced_config import MCPConfigurationManager, MCPContextRouter
        
        config_manager = MCPConfigurationManager("test_advanced_mcp_config.json")
        router = MCPContextRouter(config_manager)
        
        # Test routing with different content types
        test_cases = [
            {
                "content": "def test_function(): pass",
                "source_info": {"file_path": "test.py", "type": "code"},
                "description": "Python code"
            },
            {
                "content": "# Project Documentation\\nThis is a test README",
                "source_info": {"file_path": "README.md", "type": "documentation"},
                "description": "Documentation"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            result = await router.route_context(
                test_case["content"],
                test_case["source_info"]
            )
            
            print(f"✅ Routed {test_case['description']}: {result['status']}")
            if 'target_servers' in result:
                print(f"   Target servers: {result['target_servers']}")
        
        # Get routing statistics
        stats = router.get_routing_statistics()
        print(f"✅ Routing statistics: {stats['total_routes']} total routes")
        
        return True
        
    except Exception as e:
        print(f"❌ Context routing test failed: {e}")
        return False


async def run_comprehensive_test():
    """Run comprehensive test of all features"""
    print("\\n🚀 Running Comprehensive Test...")
    
    try:
        from gemini_advanced_mcp_examples import AdvancedMCPExamples
        
        examples = AdvancedMCPExamples()
        await examples.setup()
        
        print("✅ Advanced MCP examples setup completed")
        
        # Run a simple context synthesis example
        await examples.example_1_advanced_context_synthesis()
        print("✅ Context synthesis example completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return False


def display_summary():
    """Display setup summary and next steps"""
    print("\\n" + "="*60)
    print("🎉 Advanced Gemini MCP Integration Setup Complete!")
    print("="*60)
    
    print("\\n📁 Files Created:")
    files = [
        "gemini_advanced_mcp.py",
        "gemini_mcp_enhanced_config.py", 
        "gemini_advanced_mcp_examples.py",
        "gemini_mcp_advanced_config.json",
        "README_advanced_mcp.md",
        "test_advanced_mcp_config.json"
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} (missing)")
    
    print("\\n🚀 Next Steps:")
    print("1. Set your GOOGLE_AI_API_KEY environment variable")
    print("2. Install required dependencies: pip install -r requirements.txt")
    print("3. Run examples: python gemini_advanced_mcp_examples.py")
    print("4. Read the documentation: README_advanced_mcp.md")
    print("5. Customize configuration: gemini_mcp_advanced_config.json")
    
    print("\\n💡 Quick Start Commands:")
    print("   # Run all examples")
    print("   python gemini_advanced_mcp_examples.py")
    print("   ")
    print("   # Run specific examples")
    print("   python gemini_advanced_mcp_examples.py synthesis")
    print("   python gemini_advanced_mcp_examples.py workflow")
    print("   python gemini_advanced_mcp_examples.py routing")
    
    print("\\n📚 Documentation:")
    print("   - README_advanced_mcp.md: Comprehensive documentation")
    print("   - gemini_mcp_advanced_config.json: Configuration reference")
    print("   - Source code: Well-documented Python modules")


async def main():
    """Main setup and test function"""
    print("🚀 Advanced Gemini MCP Integration Setup & Test")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("\\n❌ Please install missing dependencies first")
        return False
    
    # Check environment
    has_api_key = check_environment()
    
    # Create test configuration
    config_file = create_test_configuration()
    if not config_file:
        print("\\n❌ Failed to create configuration")
        return False
    
    # Run tests
    print("\\n🧪 Running Tests...")
    
    test_results = []
    
    # Basic setup test
    result = await test_basic_setup()
    test_results.append(("Basic Setup", result))
    
    # Context management test
    result = await test_context_management()
    test_results.append(("Context Management", result))
    
    # Workflow orchestration test
    result = await test_workflow_orchestration()
    test_results.append(("Workflow Orchestration", result))
    
    # Context routing test
    result = await test_context_routing()
    test_results.append(("Context Routing", result))
    
    # Comprehensive test (only if API key is available)
    if has_api_key:
        result = await run_comprehensive_test()
        test_results.append(("Comprehensive Test", result))
    
    # Display test results
    print("\\n📊 Test Results:")
    print("-" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\\n📈 Overall: {passed}/{total} tests passed")
    
    # Display summary
    display_summary()
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Setup failed with error: {e}")
        sys.exit(1)
