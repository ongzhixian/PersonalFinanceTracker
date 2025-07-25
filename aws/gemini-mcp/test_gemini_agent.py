"""
Test script to verify Gemini AI Agent setup
"""

import sys
import os


def test_imports():
    """Test if all required imports are available"""
    print("🔍 Testing imports...")
    
    try:
        import json
        print("✅ json - OK")
    except ImportError as e:
        print(f"❌ json - FAILED: {e}")
        return False
    
    try:
        from google import genai
        print("✅ google.genai - OK")
    except ImportError as e:
        print(f"❌ google.genai - FAILED: {e}")
        print("   Install with: pip install google-genai")
        return False
    
    try:
        from google.genai import types
        print("✅ google.genai.types - OK")
    except ImportError as e:
        print(f"❌ google.genai.types - FAILED: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL (Pillow) - OK")
    except ImportError as e:
        print(f"❌ PIL (Pillow) - FAILED: {e}")
        print("   Install with: pip install pillow")
        return False
    
    return True


def test_api_key():
    """Test if API key is available"""
    print("\n🔑 Testing API key...")
    
    # Check environment variables
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print("✅ API key found in environment variables")
        return True
    
    # Check user secrets
    try:
        user_secrets_id = 'tech-notes-press'
        user_secrets_path = os.path.expandvars(
            f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json'
        )
        
        if os.path.exists(user_secrets_path):
            import json
            with open(user_secrets_path) as f:
                secrets = json.load(f)
            
            if 'hci_blazer_gemini_api_key' in secrets:
                print("✅ API key found in user secrets")
                return True
    except Exception as e:
        print(f"⚠️  Error checking user secrets: {e}")
    
    print("❌ API key not found")
    print("   Set environment variable: GEMINI_API_KEY=your_api_key")
    print("   Or add to user secrets: hci_blazer_gemini_api_key")
    return False


def test_agent_creation():
    """Test if the agent can be created"""
    print("\n🤖 Testing agent creation...")
    
    try:
        from gemini_agent import GeminiAgent
        
        # Try to create agent (this will test API key)
        agent = GeminiAgent()
        print("✅ Gemini Agent created successfully")
        
        # Test basic functionality
        stats = agent.get_stats()
        print(f"✅ Agent stats: {stats['total_interactions']} interactions")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


def run_quick_test():
    """Run a quick test of the agent"""
    print("\n⚡ Running quick test...")
    
    try:
        from gemini_agent import GeminiAgent
        
        agent = GeminiAgent()
        response = agent.generate_text("Say hello in a creative way (keep it short)")
        print(f"✅ Test response: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Gemini AI Agent Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test API key
    if not test_api_key():
        all_passed = False
    
    # Test agent creation
    if all_passed and not test_agent_creation():
        all_passed = False
    
    # Quick functionality test
    if all_passed and not run_quick_test():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your Gemini AI Agent is ready to use.")
        print("\nNext steps:")
        print("1. Run: python gemini_agent_examples.py")
        print("2. Or run: python gemini_agent.py (for interactive mode)")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install google-genai pillow")
        print("2. Set your API key: export GEMINI_API_KEY=your_api_key")
        print("3. Get API key from: https://makersuite.google.com/app/apikey")


if __name__ == "__main__":
    main()
