"""
Multi-Context Examples for Gemini AI Agent
Demonstrates various ways to handle multiple contexts
"""

from gemini_agent import GeminiAgent
import json
import os


def basic_multi_session_example():
    """Demonstrate basic multi-session functionality"""
    print("🔄 Basic Multi-Session Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Create different sessions for different topics
    agent.create_session("work", context_window=15)
    agent.create_session("personal", context_window=10)
    agent.create_session("learning", context_window=20)
    
    # Work session
    agent.switch_session("work")
    print("\n📊 Work Session:")
    response1 = agent.chat("I need help with project planning for a Python application")
    print(f"Assistant: {response1[:100]}...")
    
    response2 = agent.chat("What are the key milestones I should consider?")
    print(f"Assistant: {response2[:100]}...")
    
    # Personal session
    agent.switch_session("personal")
    print("\n🏠 Personal Session:")
    response3 = agent.chat("I want to plan a vacation to Japan")
    print(f"Assistant: {response3[:100]}...")
    
    response4 = agent.chat("What's the best time to visit?")
    print(f"Assistant: {response4[:100]}...")
    
    # Learning session
    agent.switch_session("learning")
    print("\n📚 Learning Session:")
    response5 = agent.chat("Explain machine learning concepts")
    print(f"Assistant: {response5[:100]}...")
    
    # Show session stats
    print("\n📋 Session Statistics:")
    sessions = agent.list_sessions()
    for name, info in sessions.items():
        print(f"  {name}: {info['message_count']} messages")


def merged_context_example():
    """Demonstrate merging context from multiple sessions"""
    print("\n🔗 Merged Context Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Create and populate sessions
    agent.create_session("tech_discussion")
    agent.create_session("project_planning")
    
    # Tech discussion
    agent.switch_session("tech_discussion")
    agent.chat("I'm working with Python and need to choose between FastAPI and Flask")
    agent.chat("Performance and scalability are important factors")
    
    # Project planning
    agent.switch_session("project_planning")
    agent.chat("I need to create a timeline for a web API project")
    agent.chat("The project should be completed in 3 months")
    
    # Now merge contexts for a comprehensive discussion
    print("\n🎯 Merged Context Response:")
    response = agent.chat_with_multi_session_context(
        message="Based on our previous discussions, which framework should I use and how should I structure the timeline?",
        session_names=["tech_discussion", "project_planning"],
        target_session="final_decision"
    )
    print(f"Merged Response: {response}")


def document_context_example():
    """Demonstrate using document context in conversations"""
    print("\n📄 Document Context Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Create sample documents
    tech_doc = """
    # API Design Guidelines
    
    ## RESTful Principles
    1. Use proper HTTP methods (GET, POST, PUT, DELETE)
    2. Implement proper status codes
    3. Use consistent URL patterns
    4. Version your APIs
    
    ## Security
    - Always use HTTPS
    - Implement authentication and authorization
    - Validate all inputs
    - Use rate limiting
    """
    
    project_doc = """
    # Project Requirements
    
    ## Functional Requirements
    - User authentication system
    - Data management API
    - Real-time notifications
    - Mobile-responsive interface
    
    ## Technical Requirements
    - Python-based backend
    - PostgreSQL database
    - Redis for caching
    - Docker deployment
    """
    
    # Save documents
    with open("api_guidelines.md", "w") as f:
        f.write(tech_doc)
    
    with open("project_requirements.md", "w") as f:
        f.write(project_doc)
    
    try:
        # Chat with document context
        print("\n💬 Chatting with document context:")
        response = agent.chat_with_document_context(
            message="Based on the guidelines and requirements, what's the recommended architecture?",
            document_paths=["api_guidelines.md", "project_requirements.md"]
        )
        print(f"Document-informed response: {response}")
        
    finally:
        # Clean up
        for file in ["api_guidelines.md", "project_requirements.md"]:
            if os.path.exists(file):
                os.remove(file)


def external_context_example():
    """Demonstrate adding external context data"""
    print("\n🌐 External Context Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Add external context (could be from APIs, databases, etc.)
    external_data = {
        "user_profile": {
            "experience_level": "intermediate",
            "preferred_languages": ["Python", "JavaScript"],
            "current_projects": ["web API", "data analysis tool"]
        },
        "system_info": {
            "available_resources": "8GB RAM, 4 CPU cores",
            "deployment_target": "AWS Lambda",
            "budget_constraints": "minimal cost"
        },
        "context_timestamp": "2024-07-24T14:30:00Z"
    }
    
    agent.add_external_context(external_data, "development_session")
    
    # Chat with this context
    agent.switch_session("development_session")
    response = agent.chat(
        message="What technology stack would you recommend for my new project?",
        external_context={
            "additional_constraints": {
                "timeline": "2 months",
                "team_size": 2,
                "integration_requirements": ["existing PostgreSQL database", "Stripe payments"]
            }
        }
    )
    
    print(f"Context-aware recommendation: {response}")


def contextual_summary_example():
    """Demonstrate creating contextual summaries"""
    print("\n📋 Contextual Summary Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Create sessions with varied discussions
    agent.create_session("requirements_gathering")
    agent.create_session("technical_decisions")
    agent.create_session("implementation_planning")
    
    # Requirements gathering
    agent.switch_session("requirements_gathering")
    agent.chat("We need a system to manage customer data and orders")
    agent.chat("It should handle about 1000 users initially")
    agent.chat("Integration with existing accounting software is required")
    
    # Technical decisions
    agent.switch_session("technical_decisions")
    agent.chat("Should we use microservices or monolithic architecture?")
    agent.chat("What database would be best for this scale?")
    agent.chat("We decided on PostgreSQL with a modular monolith approach")
    
    # Implementation planning
    agent.switch_session("implementation_planning")
    agent.chat("Let's break down the development phases")
    agent.chat("Phase 1: User management and authentication")
    agent.chat("Phase 2: Order management system")
    
    # Create summary
    print("\n📝 Creating comprehensive summary:")
    summary = agent.create_contextual_summary(
        session_names=["requirements_gathering", "technical_decisions", "implementation_planning"]
    )
    print(f"Project Summary:\n{summary}")


def export_import_example():
    """Demonstrate exporting and importing context"""
    print("\n💾 Export/Import Context Example")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Create a session with some history
    agent.create_session("important_discussion")
    agent.switch_session("important_discussion")
    
    agent.chat("I'm designing a new API for our mobile app")
    agent.chat("What are the key security considerations?")
    agent.chat("How should we handle user authentication?")
    
    # Export the session
    print("\n💾 Exporting session context...")
    agent.export_session_context("important_discussion", "exported_discussion.json", "json")
    agent.export_session_context("important_discussion", "exported_discussion.md", "md")
    
    # Create new agent and import
    print("\n📥 Importing context to new agent...")
    new_agent = GeminiAgent()
    new_agent.import_session_context("exported_discussion.json", "restored_discussion")
    
    # Continue conversation with restored context
    new_agent.switch_session("restored_discussion")
    response = new_agent.chat("Based on our previous discussion, what's the next step?")
    print(f"Response with restored context: {response}")
    
    # Clean up
    for file in ["exported_discussion.json", "exported_discussion.md"]:
        if os.path.exists(file):
            os.remove(file)


def advanced_context_patterns():
    """Demonstrate advanced context handling patterns"""
    print("\n🚀 Advanced Context Patterns")
    print("=" * 50)
    
    agent = GeminiAgent()
    
    # Pattern 1: Hierarchical Sessions
    print("\n🌳 Hierarchical Sessions:")
    agent.create_session("project_root")
    agent.create_session("project_frontend")
    agent.create_session("project_backend")
    agent.create_session("project_database")
    
    # Add context to each level
    agent.switch_session("project_root")
    agent.chat("We're building an e-commerce platform")
    
    agent.switch_session("project_frontend")
    agent.chat("The frontend should be React-based with TypeScript")
    
    agent.switch_session("project_backend")
    agent.chat("Backend will use Python FastAPI")
    
    agent.switch_session("project_database")
    agent.chat("PostgreSQL for main data, Redis for caching")
    
    # Pattern 2: Context Inheritance
    print("\n🔗 Context Inheritance:")
    hierarchical_response = agent.chat_with_multi_session_context(
        message="How do all these components work together?",
        session_names=["project_root", "project_frontend", "project_backend", "project_database"],
        target_session="project_integration"
    )
    print(f"Integrated view: {hierarchical_response[:200]}...")
    
    # Pattern 3: Context Filtering
    print("\n🎯 Context Filtering:")
    technical_context = agent.get_session_context("project_backend", ["chat"])
    print(f"Backend-specific context: {len(technical_context)} characters")
    
    # Show final stats
    print("\n📊 Final Session Statistics:")
    final_stats = agent.get_stats()
    print(f"Total sessions: {len(final_stats['session_stats'])}")
    print(f"Total interactions: {final_stats['total_interactions']}")


def main():
    """Run all multi-context examples"""
    print("🤖 Gemini AI Agent - Multi-Context Examples")
    print("Choose examples to run:")
    print("1. Basic multi-session")
    print("2. Merged context") 
    print("3. Document context")
    print("4. External context")
    print("5. Contextual summaries")
    print("6. Export/import context")
    print("7. Advanced patterns")
    print("8. Run all examples")
    
    choice = input("\nEnter your choice (1-8): ").strip()
    
    try:
        if choice == "1":
            basic_multi_session_example()
        elif choice == "2":
            merged_context_example()
        elif choice == "3":
            document_context_example()
        elif choice == "4":
            external_context_example()
        elif choice == "5":
            contextual_summary_example()
        elif choice == "6":
            export_import_example()
        elif choice == "7":
            advanced_context_patterns()
        elif choice == "8":
            print("🚀 Running all examples...\n")
            basic_multi_session_example()
            merged_context_example()
            document_context_example()
            external_context_example()
            contextual_summary_example()
            export_import_example()
            advanced_context_patterns()
        else:
            print("Invalid choice. Running basic example...")
            basic_multi_session_example()
            
        print("\n✅ Examples completed!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("Make sure you have set up your Gemini API key properly.")


if __name__ == "__main__":
    main()
