# Gemini AI Agent

A comprehensive Python agent for interacting with Google's Gemini AI models. This agent provides text generation, image analysis, image generation, document processing, and conversational chat capabilities.

## Features

- 🤖 **Text Generation**: Generate responses using Gemini's language models
- 💬 **Conversational Chat**: Maintain context across multiple exchanges
- 🖼️ **Image Analysis**: Analyze and describe images using Gemini Vision
- 🎨 **Image Generation**: Create images from text prompts
- 📄 **Document Processing**: Process and analyze text documents and image documents
- 📊 **Usage Statistics**: Track interactions and model usage
- 💾 **History Management**: Save and load conversation history
- ⚙️ **Configurable**: Customizable system instructions and parameters

## Installation

1. **Install required dependencies:**
   ```bash
   pip install google-genai pillow
   ```

2. **Set up your Gemini API key:**
   
   **Option 1: Environment Variable**
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   
   **Option 2: User Secrets (if using the existing pattern)**
   Add `hci_blazer_gemini_api_key` to your user secrets file at:
   `%APPDATA%/Microsoft/UserSecrets/tech-notes-press/secrets-development.json`

3. **Get your API key from Google AI Studio:**
   Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

## Quick Start

### Test Your Setup
```bash
python test_gemini_agent.py
```

### Run Examples
```bash
python gemini_agent_examples.py
```

### Interactive Mode
```bash
python gemini_agent.py
```

## Usage Examples

### Basic Text Generation
```python
from gemini_agent import GeminiAgent

agent = GeminiAgent()
response = agent.generate_text("Explain quantum computing in simple terms")
print(response)
```

### Conversational Chat
```python
agent = GeminiAgent()

# Chat maintains context
response1 = agent.chat("What's the capital of France?")
response2 = agent.chat("What's the population of that city?")  # Refers to Paris
```

### Image Generation
```python
agent = GeminiAgent()
image_path = agent.generate_image("A futuristic robot in a garden", save_path="robot.png")
print(f"Image saved to: {image_path}")
```

### Image Analysis
```python
agent = GeminiAgent()
analysis = agent.analyze_image("photo.jpg", "What do you see in this image?")
print(analysis)
```

### Document Processing
```python
agent = GeminiAgent()
summary = agent.process_document("document.txt", "Summarize the main points")
print(summary)
```

### Custom System Instructions
```python
agent = GeminiAgent()
agent.set_system_instruction("You are a helpful coding assistant specialized in Python")
response = agent.generate_text("How do I create a list in Python?")
```

## Interactive Mode Commands

When running in interactive mode, use these commands:

- `/image <prompt>` - Generate an image
- `/analyze <path>` - Analyze an image file
- `/doc <path> [question]` - Process a document
- `/history` - Show interaction statistics
- `/stats` - Show detailed statistics
- `/quit` - Exit the program

## Configuration

The agent can be configured using `gemini_agent_config.json`:

```json
{
  "models": {
    "text": "gemini-2.0-flash",
    "vision": "gemini-2.0-flash",
    "image_generation": "gemini-2.0-flash-preview-image-generation"
  },
  "default_settings": {
    "temperature": 0.7,
    "max_tokens": 1024,
    "max_retries": 3
  }
}
```

## Available Models

- **gemini-2.0-flash**: Latest fast model for text generation
- **gemini-2.0-flash-preview-image-generation**: Image generation model
- **gemini-pro**: Professional model for complex tasks

## API Reference

### GeminiAgent Class

#### Constructor
```python
GeminiAgent(api_key=None, model="gemini-2.0-flash")
```

#### Methods

- `generate_text(prompt, max_retries=3, temperature=0.7, max_tokens=1024)` - Generate text
- `chat(message, maintain_context=True)` - Conversational chat
- `analyze_image(image_path, prompt)` - Analyze an image
- `generate_image(prompt, save_path=None)` - Generate an image
- `process_document(file_path, question)` - Process a document
- `set_system_instruction(instruction)` - Set system behavior
- `save_chat_history(file_path)` - Save conversation history
- `load_chat_history(file_path)` - Load conversation history
- `clear_history()` - Clear conversation history
- `get_stats()` - Get usage statistics

## Error Handling

The agent includes comprehensive error handling with:
- Automatic retries with exponential backoff
- Detailed error logging
- Graceful fallbacks for missing dependencies

## File Structure

```
gemini_agent.py              # Main agent class
gemini_agent_examples.py     # Usage examples
test_gemini_agent.py         # Setup verification
gemini_agent_config.json     # Configuration file
README.md                    # This file
```

## Troubleshooting

### Import Errors
```bash
pip install google-genai pillow
```

### API Key Issues
1. Verify your API key is set correctly
2. Check that your API key has the necessary permissions
3. Ensure you're not hitting rate limits

### Model Availability
Some models may not be available in all regions. The agent will fall back to available models automatically.

## Contributing

Feel free to extend the agent with additional features:
- Add support for more file formats
- Implement streaming responses
- Add batch processing capabilities
- Integrate with other Google AI services

## License

This project is part of your AWS workspace and follows your existing license terms.

---

## Example Output

```
🤖 Gemini AI Agent - Interactive Mode
Commands: /image <prompt>, /analyze <path>, /doc <path> <question>, /history, /stats, /quit
------------------------------------------------------------

👤 You: Tell me about artificial intelligence

🤖 Gemini: Artificial Intelligence (AI) is a branch of computer science focused on creating intelligent machines that can perform tasks typically requiring human intelligence. This includes learning, reasoning, problem-solving, perception, and language understanding.

AI can be categorized into:
- **Narrow AI**: Designed for specific tasks (like voice assistants, recommendation systems)
- **General AI**: Hypothetical AI that could perform any intellectual task humans can do
- **Superintelligence**: AI that surpasses human intelligence in all domains

Current AI applications include machine learning, natural language processing, computer vision, robotics, and more. While we've made significant progress with narrow AI, general AI remains a future goal.

👤 You: /image A robot learning to paint
🎨 Generating image...
✅ Image saved to: gemini_generated_20240724_143022.png
```
