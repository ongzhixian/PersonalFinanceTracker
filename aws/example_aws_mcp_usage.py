"""
Example usage of the AWS MCP Server
This script demonstrates how to use the AWS MCP server in different modes
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

def run_standalone_mcp():
    """Run the MCP server in standalone mode (for MCP clients)"""
    print("Running AWS MCP Server in standalone mode...")
    print("This mode is used by MCP clients like Claude, Cursor, or other MCP-compatible tools")
    print("\nTo use with MCP Inspector:")
    print("1. Install MCP Inspector: npm install -g @modelcontextprotocol/inspector")
    print("2. Run: mcp-inspector python example_aws_fastmcp.py")
    print("\nTo use in this script:")
    
    try:
        # Import and run the MCP server
        import example_aws_fastmcp
        example_aws_fastmcp.main()
    except ImportError as e:
        print(f"Error importing AWS MCP module: {e}")
        print("Make sure you have installed the requirements: pip install -r aws_mcp_requirements.txt")
    except Exception as e:
        print(f"Error running MCP server: {e}")

def run_fastapi_mode():
    """Run the MCP server with FastAPI"""
    print("Running AWS MCP Server with FastAPI...")
    print("This mode provides a web interface and HTTP endpoints")
    print("Access the server at: http://localhost:8000")
    print("MCP endpoints at: http://localhost:8000/mcp")
    
    try:
        import uvicorn
        import example_aws_fastmcp
        
        app = example_aws_fastmcp.create_fastapi_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure you have installed the requirements: pip install -r aws_mcp_requirements.txt")
    except Exception as e:
        print(f"Error running FastAPI server: {e}")

async def test_mcp_client():
    """Test the MCP server using a simple client"""
    print("Testing AWS MCP Server with a simple client...")
    
    try:
        from fastmcp import Client
        
        # This would connect to a running MCP server
        # For demonstration purposes, we'll show what the client code would look like
        print("""
Example client code:

```python
from fastmcp import Client
import asyncio

async def test_aws_mcp():
    # Connect to the MCP server
    async with Client("stdio", "python", "example_aws_fastmcp.py") as client:
        
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])
        
        # List available resources
        resources = await client.list_resources()
        print("Available resources:", [resource.uri for resource in resources])
        
        # Call a tool
        result = await client.call_tool("list_s3_buckets")
        print("S3 Buckets:", result)
        
        # Read a resource
        version_resource = await client.read_resource("aws-mcp://version")
        print("Server version:", version_resource.contents[0].text)

# Run the test
asyncio.run(test_aws_mcp())
```
        """)
        
    except ImportError:
        print("FastMCP client not available. Install with: pip install fastmcp")

def show_available_tools():
    """Show all available tools and resources in the AWS MCP server"""
    print("AWS MCP Server - Available Tools and Resources")
    print("=" * 50)
    
    tools = [
        "list_s3_buckets - List all S3 buckets in the account",
        "list_s3_objects - List objects in an S3 bucket",
        "create_s3_bucket - Create a new S3 bucket",
        "list_ec2_instances - List EC2 instances in a region",
        "get_ec2_instance_details - Get detailed EC2 instance information",
        "list_lambda_functions - List Lambda functions in a region",
        "get_lambda_function_details - Get detailed Lambda function information",
        "list_dynamodb_tables - List DynamoDB tables in a region",
        "get_dynamodb_table_details - Get detailed DynamoDB table information",
        "list_iam_users - List IAM users in the account",
        "list_iam_roles - List IAM roles in the account",
        "get_cloudwatch_metrics - Get CloudWatch metrics for a namespace",
        "list_cloudwatch_log_groups - List CloudWatch log groups",
        "get_aws_account_info - Get AWS account information",
        "estimate_aws_costs - Get estimated AWS costs (requires Cost Explorer)"
    ]
    
    resources = [
        "aws-mcp://version - Server version information",
        "aws-mcp://aws-regions - List of all AWS regions",
        "aws-mcp://aws-services - List of supported AWS services",
        "aws-mcp://s3/bucket/{bucket_name}/info - S3 bucket information"
    ]
    
    print("\nTools:")
    for tool in tools:
        print(f"  â€¢ {tool}")
    
    print("\nResources:")
    for resource in resources:
        print(f"  â€¢ {resource}")
    
    print("\nAWS Services Supported:")
    services = [
        "S3 - Simple Storage Service",
        "EC2 - Elastic Compute Cloud",
        "Lambda - Serverless Functions",
        "DynamoDB - NoSQL Database",
        "IAM - Identity and Access Management",
        "CloudWatch - Monitoring and Logs",
        "STS - Security Token Service",
        "Cost Explorer - Cost Analysis (optional)"
    ]
    
    for service in services:
        print(f"  â€¢ {service}")

def main():
    """Main function to run examples"""
    print("AWS MCP Server Examples")
    print("=" * 30)
    
    while True:
        print("\nChoose an option:")
        print("1. Show available tools and resources")
        print("2. Run MCP server in standalone mode")
        print("3. Run MCP server with FastAPI")
        print("4. Show example client code")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            show_available_tools()
        elif choice == "2":
            run_standalone_mcp()
            break
        elif choice == "3":
            run_fastapi_mode()
            break
        elif choice == "4":
            asyncio.run(test_mcp_client())
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
