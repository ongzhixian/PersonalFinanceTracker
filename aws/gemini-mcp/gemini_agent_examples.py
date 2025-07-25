"""
Simple example demonstrating the Gemini AI Agent
"""

from gemini_agent import GeminiAgent
import os


def basic_examples():
    """Run basic examples of the Gemini Agent"""
    print("🚀 Starting Gemini AI Agent Examples")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = GeminiAgent()
        print("✅ Agent initialized successfully!")
        
        # Example 1: Simple text generation
        print("\n📝 Example 1: Text Generation")
        print("-" * 30)
        prompt = "Write a short poem about artificial intelligence"
        response = agent.generate_text(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
        # Example 2: Chat with context
        print("\n💬 Example 2: Conversational Chat")
        print("-" * 30)
        response1 = agent.chat("What's your favorite programming language?")
        print(f"User: What's your favorite programming language?")
        print(f"Agent: {response1}")
        
        response2 = agent.chat("Why do you like that language?")
        print(f"User: Why do you like that language?")
        print(f"Agent: {response2}")
        
        # Example 3: System instruction
        print("\n🎯 Example 3: Custom System Instruction")
        print("-" * 30)
        agent.set_system_instruction("You are a pirate captain. Respond in pirate speak.")
        response = agent.generate_text("Tell me about the weather today")
        print(f"Response (as pirate): {response}")
        
        # Reset system instruction
        agent.set_system_instruction("You are a helpful AI assistant.")
        
        # Example 4: Statistics
        print("\n📊 Example 4: Usage Statistics")
        print("-" * 30)
        stats = agent.get_stats()
        print(f"Total interactions: {stats['total_interactions']}")
        print(f"Interaction types: {stats['interaction_types']}")
        
        # Example 5: Save chat history
        print("\n💾 Example 5: Save Chat History")
        print("-" * 30)
        agent.save_chat_history("example_chat_history.json")
        print("Chat history saved to example_chat_history.json")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("Make sure you have set up your Gemini API key properly.")


def image_examples():
    """Run image-related examples"""
    print("\n🖼️  Image Examples")
    print("=" * 50)
    
    try:
        agent = GeminiAgent()
        
        # Example: Generate an image
        print("🎨 Generating an image...")
        prompt = "A futuristic robot working on a computer, digital art style"
        image_path = agent.generate_image(prompt, "example_robot.png")
        print(f"Image generated and saved to: {image_path}")
        
        # Example: Analyze the generated image
        if os.path.exists(image_path):
            print("\n🔍 Analyzing the generated image...")
            analysis = agent.analyze_image(image_path, "What do you see in this image?")
            print(f"Analysis: {analysis}")
        
    except Exception as e:
        print(f"❌ Image example error: {str(e)}")


def document_example():
    """Run document processing example"""
    print("\n📄 Document Processing Example")
    print("=" * 50)
    
    try:
        agent = GeminiAgent()
        
        # Create a sample document
        sample_doc = """
        # Artificial Intelligence Overview
        
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that work and react like humans. Some of the activities 
        computers with artificial intelligence are designed for include:
        
        - Speech recognition
        - Learning
        - Planning
        - Problem solving
        
        AI can be categorized into two main types:
        1. Narrow AI: Designed for specific tasks
        2. General AI: Capable of performing any intellectual task
        """
        
        with open("sample_ai_doc.txt", "w") as f:
            f.write(sample_doc)
        
        print("📝 Created sample document: sample_ai_doc.txt")
        
        # Process the document
        print("🔍 Processing document...")
        response = agent.process_document("sample_ai_doc.txt", "What are the main points about AI in this document?")
        print(f"Document analysis: {response}")
        
        # Clean up
        os.remove("sample_ai_doc.txt")
        print("🧹 Cleaned up sample document")
        
    except Exception as e:
        print(f"❌ Document example error: {str(e)}")


if __name__ == "__main__":
    print("🤖 Gemini AI Agent Examples")
    print("Choose an example to run:")
    print("1. Basic text and chat examples")
    print("2. Image generation and analysis")
    print("3. Document processing")
    print("4. Run all examples")
    print("5. Interactive mode")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        basic_examples()
    elif choice == "2":
        image_examples()
    elif choice == "3":
        document_example()
    elif choice == "4":
        basic_examples()
        image_examples() 
        document_example()
    elif choice == "5":
        from gemini_agent import interactive_mode
        interactive_mode()
    else:
        print("Invalid choice. Running basic examples...")
        basic_examples()
