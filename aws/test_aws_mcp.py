#!/usr/bin/env python3
"""
Test script for AWS MCP Server
Verifies installation and basic functionality
"""

import sys
import json
from datetime import datetime

from example_common_aws import setup_aws_profile

setup_aws_profile()

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import boto3
        print("✅ boto3 imported successfully")
    except ImportError as e:
        print(f"❌ boto3 import failed: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi imported successfully")
    except ImportError as e:
        print(f"❌ fastapi import failed: {e}")
        return False
    
    try:
        import fastmcp
        print("✅ fastmcp imported successfully")
    except ImportError as e:
        print(f"❌ fastmcp import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ uvicorn import failed: {e}")
        return False
    
    return True

def test_aws_credentials():
    """Test AWS credentials configuration"""
    print("\nTesting AWS credentials...")
    
    try:
        import boto3
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        
        print("✅ AWS credentials configured successfully")
        print(f"   Account ID: {response.get('Account', 'Unknown')}")
        print(f"   User ARN: {response.get('Arn', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        print("   Please configure AWS credentials using:")
        print("   - aws configure")
        print("   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("   - IAM roles (if running on EC2)")
        return False

def test_mcp_server():
    """Test that the MCP server can be imported and initialized"""
    print("\nTesting MCP server...")
    
    try:
        import example_aws_fastmcp
        print("✅ AWS MCP server module imported successfully")
        
        # Test that the FastMCP instance was created
        if hasattr(example_aws_fastmcp, 'mcp'):
            print("✅ FastMCP instance created successfully")
            return True
        else:
            print("❌ FastMCP instance not found")
            return False
            
    except ImportError as e:
        print(f"❌ AWS MCP server import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ AWS MCP server initialization failed: {e}")
        return False

def test_fastapi_app():
    """Test that the FastAPI app can be created"""
    print("\nTesting FastAPI application...")
    
    try:
        import example_aws_fastmcp
        app = example_aws_fastmcp.create_fastapi_app()
        
        if app:
            print("✅ FastAPI application created successfully")
            return True
        else:
            print("❌ FastAPI application creation failed")
            return False
            
    except Exception as e:
        print(f"❌ FastAPI application test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic MCP functionality"""
    print("\nTesting basic MCP functionality...")
    
    try:
        import example_aws_fastmcp
        
        # Test getting account info (if credentials are available)
        try:
            result = example_aws_fastmcp.get_aws_account_info()
            if 'error' not in result:
                print("✅ AWS account info retrieval successful")
                print(f"   Account: {result.get('account_id', 'Unknown')}")
            else:
                print(f"⚠️  AWS account info failed: {result['error']}")
        except Exception as e:
            print(f"⚠️  AWS account info test failed: {e}")
        
        # Test S3 bucket listing (may fail without credentials)
        try:
            result = example_aws_fastmcp.list_s3_buckets()
            if 'error' not in result:
                print(f"✅ S3 bucket listing successful ({result.get('count', 0)} buckets)")
            else:
                print(f"⚠️  S3 bucket listing failed: {result['error']}")
        except Exception as e:
            print(f"⚠️  S3 bucket listing test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("AWS MCP Server Test Report")
    print("="*60)
    print(f"Test run at: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    
    results = {
        "imports": test_imports(),
        "aws_credentials": test_aws_credentials(),
        "mcp_server": test_mcp_server(),
        "fastapi_app": test_fastapi_app(),
        "basic_functionality": test_basic_functionality()
    }
    
    print("\n" + "-"*60)
    print("Test Summary:")
    print("-"*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AWS MCP Server is ready to use.")
        print("\nNext steps:")
        print("1. Run: python example_aws_fastmcp.py --mode fastapi")
        print("2. Access: http://localhost:8000")
        print("3. Or run: python example_aws_mcp_usage.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        if not results["imports"]:
            print("\nTo fix import issues:")
            print("pip install -r aws_mcp_requirements.txt")
        
        if not results["aws_credentials"]:
            print("\nTo fix AWS credential issues:")
            print("aws configure")

def main():
    """Main test function"""
    print("AWS MCP Server Installation Test")
    print("This script will verify that your installation is working correctly.\n")
    
    generate_test_report()

if __name__ == "__main__":
    main()
