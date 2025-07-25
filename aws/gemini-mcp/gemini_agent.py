"""
Gemini AI Agent - A comprehensive Python agent for interacting with Google's Gemini AI
Features:
- Text generation and chat
- Image analysis and generation
- File processing
- Conversation history management
- Multiple model support
- Error handling and retry logic
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install: pip install google-genai pillow")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiAgent:
    """A comprehensive agent for interacting with Google's Gemini AI models"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        """
        Initialize the Gemini Agent
        
        Args:
            api_key: Google AI API key
            model: Model to use (default: gemini-2.0-flash)
        """
        self.api_key = api_key or self._get_api_key()
        self.model = model
        self.client = genai.Client(api_key=self.api_key)
        self.chat_history: List[Dict[str, Any]] = []
        self.system_instruction = "You are a helpful AI assistant."
        
        # Multi-context support
        self.conversation_sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.current_session = "default"
        self.context_windows: Dict[str, int] = {
            "default": 10,
            "long": 50,
            "short": 5
        }
        
        # Available models
        self.models = {
            "text": "gemini-2.0-flash",
            "vision": "gemini-2.0-flash", 
            "image_gen": "gemini-2.0-flash-preview-image-generation",
            "pro": "gemini-pro"
        }
        
        logger.info(f"Gemini Agent initialized with model: {self.model}")
    
    def _get_api_key(self) -> str:
        """Get API key from secrets or environment"""
        try:
            # Try to get from user secrets first
            secrets = self._get_secrets_dict()
            if 'hci_blazer_gemini_api_key' in secrets:
                return secrets['hci_blazer_gemini_api_key']
        except:
            pass
        
        # Fallback to environment variable
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment variable "
                "or add 'hci_blazer_gemini_api_key' to your user secrets."
            )
        return api_key
    
    def _get_secrets_dict(self) -> Dict[str, Any]:
        """Load secrets from user secrets file"""
        user_secrets_id = 'tech-notes-press'
        user_secrets_path = os.path.expandvars(
            f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json'
        )
        
        if os.path.exists(user_secrets_path):
            with open(user_secrets_path) as f:
                return json.load(f)
        return {}
    
    def set_system_instruction(self, instruction: str):
        """Set system instruction for the agent"""
        self.system_instruction = instruction
        logger.info(f"System instruction updated: {instruction[:50]}...")
    
    # Context Management Methods
    
    def create_session(self, session_name: str, context_window: int = 10) -> str:
        """
        Create a new conversation session
        
        Args:
            session_name: Name of the session
            context_window: Number of exchanges to maintain in context
            
        Returns:
            Session name
        """
        self.conversation_sessions[session_name] = []
        self.context_windows[session_name] = context_window
        logger.info(f"Created session '{session_name}' with context window {context_window}")
        return session_name
    
    def switch_session(self, session_name: str) -> bool:
        """
        Switch to a different conversation session
        
        Args:
            session_name: Name of session to switch to
            
        Returns:
            True if successful, False if session doesn't exist
        """
        if session_name in self.conversation_sessions:
            self.current_session = session_name
            logger.info(f"Switched to session '{session_name}'")
            return True
        else:
            logger.warning(f"Session '{session_name}' does not exist")
            return False
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all conversation sessions with their info
        
        Returns:
            Dictionary of session info
        """
        sessions_info = {}
        for session_name, history in self.conversation_sessions.items():
            sessions_info[session_name] = {
                "message_count": len(history),
                "context_window": self.context_windows.get(session_name, 10),
                "is_current": session_name == self.current_session,
                "last_interaction": history[-1]["timestamp"] if history else None
            }
        
        # Add main history if it exists
        if self.chat_history:
            sessions_info["main"] = {
                "message_count": len(self.chat_history),
                "context_window": 10,
                "is_current": self.current_session == "default",
                "last_interaction": self.chat_history[-1]["timestamp"]
            }
        
        return sessions_info
    
    def get_session_context(self, session_name: str = None, context_types: List[str] = None) -> str:
        """
        Get formatted context from a specific session
        
        Args:
            session_name: Session to get context from (current if None)
            context_types: Types of interactions to include (chat, text_generation, etc.)
            
        Returns:
            Formatted context string
        """
        if session_name is None:
            session_name = self.current_session
        
        # Get history from appropriate source
        if session_name == "main" or session_name == "default":
            history = self.chat_history
        else:
            history = self.conversation_sessions.get(session_name, [])
        
        if not history:
            return ""
        
        # Filter by context types if specified
        if context_types:
            history = [entry for entry in history if entry.get("type") in context_types]
        
        # Get context window
        context_window = self.context_windows.get(session_name, 10)
        recent_history = history[-context_window:]
        
        # Format context
        context_lines = []
        for entry in recent_history:
            entry_type = entry.get("type", "unknown")
            timestamp = entry.get("timestamp", "")
            
            if entry_type == "chat":
                context_lines.append(f"[{timestamp}] User: {entry.get('message', '')}")
                context_lines.append(f"[{timestamp}] Assistant: {entry.get('response', '')}")
            elif entry_type == "text_generation":
                context_lines.append(f"[{timestamp}] Generated: {entry.get('response', '')[:100]}...")
            elif entry_type == "image_analysis":
                context_lines.append(f"[{timestamp}] Image Analysis: {entry.get('response', '')[:100]}...")
        
        return "\n".join(context_lines)
    
    def merge_contexts(self, session_names: List[str], max_entries: int = 20) -> str:
        """
        Merge context from multiple sessions
        
        Args:
            session_names: List of session names to merge
            max_entries: Maximum number of entries to include
            
        Returns:
            Merged context string
        """
        all_entries = []
        
        for session_name in session_names:
            if session_name == "main" or session_name == "default":
                history = self.chat_history
            else:
                history = self.conversation_sessions.get(session_name, [])
            
            for entry in history:
                entry_with_session = entry.copy()
                entry_with_session["session"] = session_name
                all_entries.append(entry_with_session)
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x.get("timestamp", ""))
        
        # Take most recent entries
        recent_entries = all_entries[-max_entries:]
        
        # Format merged context
        context_lines = []
        for entry in recent_entries:
            session = entry.get("session", "unknown")
            timestamp = entry.get("timestamp", "")
            entry_type = entry.get("type", "unknown")
            
            if entry_type == "chat":
                context_lines.append(f"[{session}:{timestamp}] User: {entry.get('message', '')}")
                context_lines.append(f"[{session}:{timestamp}] Assistant: {entry.get('response', '')}")
        
        return "\n".join(context_lines)
    
    def add_external_context(self, context_data: Dict[str, Any], session_name: str = None):
        """
        Add external context data to a session
        
        Args:
            context_data: External context information
            session_name: Session to add context to (current if None)
        """
        if session_name is None:
            session_name = self.current_session
        
        context_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "external_context",
            "context_data": context_data,
            "model": self.model
        }
        
        if session_name == "main" or session_name == "default":
            self.chat_history.append(context_entry)
        else:
            if session_name not in self.conversation_sessions:
                self.create_session(session_name)
            self.conversation_sessions[session_name].append(context_entry)
        
        logger.info(f"Added external context to session '{session_name}'")
    
    def generate_text(self, 
                     prompt: str, 
                     max_retries: int = 3,
                     temperature: float = 0.7,
                     max_tokens: int = 1024) -> str:
        """
        Generate text response from Gemini
        
        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        for attempt in range(max_retries):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt],
                    config=config
                )
                
                if response.candidates and response.candidates[0].content.parts:
                    result = response.candidates[0].content.parts[0].text
                    
                    # Add to chat history
                    self.chat_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "text_generation",
                        "prompt": prompt,
                        "response": result,
                        "model": self.model
                    })
                    
                    return result
                else:
                    raise Exception("No valid response generated")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate text after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def chat(self, message: str, 
             maintain_context: bool = True, 
             session_name: str = None,
             context_sources: List[str] = None,
             external_context: Dict[str, Any] = None) -> str:
        """
        Have a conversation with Gemini maintaining context
        
        Args:
            message: User message
            maintain_context: Whether to maintain conversation context
            session_name: Specific session to use (current session if None)
            context_sources: List of sessions to pull context from
            external_context: Additional context data to include
            
        Returns:
            AI response
        """
        try:
            if session_name is None:
                session_name = self.current_session
            
            full_prompt = message
            
            if maintain_context:
                context_parts = []
                
                # Add external context if provided
                if external_context:
                    context_parts.append(f"Additional Context: {json.dumps(external_context, indent=2)}")
                
                # Build conversation context
                if context_sources:
                    # Merge context from multiple sources
                    merged_context = self.merge_contexts(context_sources)
                    if merged_context:
                        context_parts.append(f"Previous conversations:\n{merged_context}")
                else:
                    # Use single session context
                    session_context = self.get_session_context(session_name, ["chat"])
                    if session_context:
                        context_parts.append(f"Previous conversation:\n{session_context}")
                
                if context_parts:
                    full_prompt = "\n\n".join(context_parts) + f"\n\nUser: {message}"
            
            response = self.generate_text(full_prompt)
            
            # Update appropriate chat history
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "chat",
                "message": message,
                "response": response,
                "model": self.model,
                "session": session_name
            }
            
            if external_context:
                chat_entry["external_context"] = external_context
            
            if session_name == "main" or session_name == "default":
                self.chat_history.append(chat_entry)
            else:
                if session_name not in self.conversation_sessions:
                    self.create_session(session_name)
                self.conversation_sessions[session_name].append(chat_entry)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """
        Analyze an image using Gemini Vision
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            
        Returns:
            Image analysis response
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create image part
            image_part = types.Part.from_bytes(
                data=image_data,
                mime_type=self._get_mime_type(image_path)
            )
            
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction
            )
            
            response = self.client.models.generate_content(
                model=self.models["vision"],
                contents=[prompt, image_part],
                config=config
            )
            
            if response.candidates and response.candidates[0].content.parts:
                result = response.candidates[0].content.parts[0].text
                
                # Add to history
                self.chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "image_analysis",
                    "image_path": image_path,
                    "prompt": prompt,
                    "response": result,
                    "model": self.models["vision"]
                })
                
                return result
            else:
                raise Exception("No valid response for image analysis")
                
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            raise
    
    def generate_image(self, prompt: str, save_path: str = None) -> str:
        """
        Generate an image using Gemini
        
        Args:
            prompt: Image generation prompt
            save_path: Path to save generated image
            
        Returns:
            Path to saved image or base64 encoded image data
        """
        try:
            response = self.client.models.generate_content(
                model=self.models["image_gen"],
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            image_data = None
            text_response = ""
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                elif part.inline_data is not None:
                    image_data = part.inline_data.data
            
            if image_data:
                image = Image.open(BytesIO(image_data))
                
                if save_path:
                    image.save(save_path)
                    result_path = save_path
                else:
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    result_path = f"gemini_generated_{timestamp}.png"
                    image.save(result_path)
                
                # Add to history
                self.chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "image_generation",
                    "prompt": prompt,
                    "response": text_response,
                    "image_path": result_path,
                    "model": self.models["image_gen"]
                })
                
                logger.info(f"Image generated and saved to: {result_path}")
                return result_path
            else:
                raise Exception("No image data received")
                
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise
    
    def process_document(self, file_path: str, question: str = "Summarize this document") -> str:
        """
        Process and analyze a document
        
        Args:
            file_path: Path to document file
            question: Question about the document
            
        Returns:
            Document analysis response
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.txt', '.md']:
                # Text file processing
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                prompt = f"Document content:\n{content}\n\nQuestion: {question}"
                return self.generate_text(prompt)
                
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                # Image document processing
                return self.analyze_image(file_path, question)
                
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            raise
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def save_chat_history(self, file_path: str = None):
        """Save chat history to JSON file"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"gemini_chat_history_{timestamp}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Chat history saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save chat history: {str(e)}")
    
    def load_chat_history(self, file_path: str):
        """Load chat history from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)
            logger.info(f"Chat history loaded from: {file_path}")
        except Exception as e:
            logger.error(f"Failed to load chat history: {str(e)}")
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        logger.info("Chat history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_interactions = len(self.chat_history)
        type_counts = {}
        
        for entry in self.chat_history:
            entry_type = entry.get("type", "unknown")
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        # Add session stats
        session_stats = {}
        for session_name, history in self.conversation_sessions.items():
            session_type_counts = {}
            for entry in history:
                entry_type = entry.get("type", "unknown")
                session_type_counts[entry_type] = session_type_counts.get(entry_type, 0) + 1
            
            session_stats[session_name] = {
                "total_interactions": len(history),
                "interaction_types": session_type_counts,
                "context_window": self.context_windows.get(session_name, 10)
            }
        
        return {
            "total_interactions": total_interactions,
            "interaction_types": type_counts,
            "current_model": self.model,
            "available_models": self.models,
            "current_session": self.current_session,
            "session_stats": session_stats
        }
    
    # Advanced Context Methods
    
    def chat_with_document_context(self, message: str, document_paths: List[str], session_name: str = None) -> str:
        """
        Chat with document context loaded
        
        Args:
            message: User message
            document_paths: List of document paths to load as context
            session_name: Session to use
            
        Returns:
            AI response with document context
        """
        try:
            # Load document contents
            document_context = {}
            for doc_path in document_paths:
                if os.path.exists(doc_path):
                    file_ext = Path(doc_path).suffix.lower()
                    if file_ext in ['.txt', '.md']:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            document_context[doc_path] = f.read()
                    else:
                        document_context[doc_path] = f"[Binary file: {doc_path}]"
            
            return self.chat(
                message=message,
                session_name=session_name,
                external_context={"documents": document_context}
            )
            
        except Exception as e:
            logger.error(f"Document context chat error: {str(e)}")
            return f"Error loading document context: {str(e)}"
    
    def chat_with_multi_session_context(self, message: str, session_names: List[str], target_session: str = None) -> str:
        """
        Chat with context from multiple sessions
        
        Args:
            message: User message
            session_names: List of session names to pull context from
            target_session: Session to store the response in
            
        Returns:
            AI response with multi-session context
        """
        return self.chat(
            message=message,
            session_name=target_session,
            context_sources=session_names
        )
    
    def create_contextual_summary(self, session_names: List[str] = None, max_entries: int = 50) -> str:
        """
        Create a summary of conversation context across sessions
        
        Args:
            session_names: Sessions to summarize (all if None)
            max_entries: Maximum entries to include
            
        Returns:
            Summary of conversations
        """
        try:
            if session_names is None:
                session_names = list(self.conversation_sessions.keys()) + ["main"]
            
            merged_context = self.merge_contexts(session_names, max_entries)
            
            if not merged_context:
                return "No conversation history found."
            
            summary_prompt = f"""
            Please provide a concise summary of the following conversation history:
            
            {merged_context}
            
            Focus on:
            1. Main topics discussed
            2. Key decisions or conclusions
            3. Ongoing questions or themes
            4. Important context for future conversations
            """
            
            return self.generate_text(summary_prompt)
            
        except Exception as e:
            logger.error(f"Summary creation error: {str(e)}")
            return f"Error creating summary: {str(e)}"
    
    def export_session_context(self, session_name: str, file_path: str = None, format_type: str = "json"):
        """
        Export session context to file
        
        Args:
            session_name: Session to export
            file_path: Path to save file (auto-generated if None)
            format_type: Export format (json, txt, md)
        """
        try:
            if session_name == "main" or session_name == "default":
                history = self.chat_history
            else:
                history = self.conversation_sessions.get(session_name, [])
            
            if not history:
                logger.warning(f"No history found for session '{session_name}'")
                return
            
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{session_name}_context_{timestamp}.{format_type}"
            
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
            
            elif format_type == "txt":
                with open(file_path, 'w', encoding='utf-8') as f:
                    for entry in history:
                        f.write(f"[{entry.get('timestamp', '')}] {entry.get('type', '')}\n")
                        if entry.get('type') == 'chat':
                            f.write(f"User: {entry.get('message', '')}\n")
                            f.write(f"Assistant: {entry.get('response', '')}\n")
                        f.write("-" * 50 + "\n")
            
            elif format_type == "md":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Conversation History: {session_name}\n\n")
                    for entry in history:
                        timestamp = entry.get('timestamp', '')
                        f.write(f"## {timestamp}\n\n")
                        if entry.get('type') == 'chat':
                            f.write(f"**User:** {entry.get('message', '')}\n\n")
                            f.write(f"**Assistant:** {entry.get('response', '')}\n\n")
                        f.write("---\n\n")
            
            logger.info(f"Session '{session_name}' exported to: {file_path}")
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
    
    def import_session_context(self, file_path: str, session_name: str):
        """
        Import session context from file
        
        Args:
            file_path: Path to context file
            session_name: Session to import into
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Context file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_history = json.load(f)
            
            if session_name not in self.conversation_sessions:
                self.create_session(session_name)
            
            self.conversation_sessions[session_name].extend(imported_history)
            logger.info(f"Imported {len(imported_history)} entries to session '{session_name}'")
            
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
    
    # ...existing code...
def interactive_mode():
    """Run the agent in interactive mode"""
    print("🤖 Gemini AI Agent - Interactive Mode with Multi-Context Support")
    print("Commands:")
    print("  /image <prompt>           - Generate an image")
    print("  /analyze <path>           - Analyze an image")
    print("  /doc <path> [question]    - Process a document")
    print("  /session <name>           - Create/switch to session")
    print("  /list-sessions            - List all sessions")
    print("  /merge <session1,session2> - Chat with merged context")
    print("  /doc-chat <doc1,doc2>     - Chat with document context")
    print("  /summary [sessions]       - Create contextual summary")
    print("  /export <session> [format] - Export session (json/txt/md)")
    print("  /history                  - Show interaction statistics")
    print("  /stats                    - Show detailed statistics")
    print("  /quit                     - Exit the program")
    print("-" * 70)
    
    agent = GeminiAgent()
    agent.create_session("default")  # Create default session
    
    while True:
        try:
            current_session = agent.current_session
            user_input = input(f"\n👤 [{current_session}] You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['/quit', '/exit']:
                print("👋 Goodbye!")
                break
                
            elif user_input.startswith('/image '):
                prompt = user_input[7:]
                print("🎨 Generating image...")
                image_path = agent.generate_image(prompt)
                print(f"✅ Image saved to: {image_path}")
                
            elif user_input.startswith('/analyze '):
                image_path = user_input[9:]
                print("🔍 Analyzing image...")
                result = agent.analyze_image(image_path)
                print(f"🤖 Gemini: {result}")
                
            elif user_input.startswith('/doc '):
                parts = user_input[5:].split(' ', 1)
                if len(parts) == 2:
                    file_path, question = parts
                else:
                    file_path = parts[0]
                    question = "Summarize this document"
                
                print("📄 Processing document...")
                result = agent.process_document(file_path, question)
                print(f"🤖 Gemini: {result}")
            
            elif user_input.startswith('/session '):
                session_name = user_input[9:].strip()
                if session_name:
                    if session_name in agent.conversation_sessions:
                        agent.switch_session(session_name)
                        print(f"🔄 Switched to session '{session_name}'")
                    else:
                        agent.create_session(session_name)
                        agent.switch_session(session_name)
                        print(f"✨ Created and switched to session '{session_name}'")
                else:
                    print("❌ Please provide a session name")
            
            elif user_input == '/list-sessions':
                sessions = agent.list_sessions()
                print("📋 Available sessions:")
                for name, info in sessions.items():
                    current_marker = " (current)" if info["is_current"] else ""
                    print(f"   {name}: {info['message_count']} messages, "
                          f"window={info['context_window']}{current_marker}")
            
            elif user_input.startswith('/merge '):
                session_list = user_input[7:].strip()
                if session_list:
                    sessions = [s.strip() for s in session_list.split(',')]
                    message = input("Enter your message: ")
                    print("� Merging context from multiple sessions...")
                    result = agent.chat_with_multi_session_context(message, sessions)
                    print(f"🤖 Gemini: {result}")
                else:
                    print("❌ Please provide session names separated by commas")
            
            elif user_input.startswith('/doc-chat '):
                doc_list = user_input[10:].strip()
                if doc_list:
                    docs = [d.strip() for d in doc_list.split(',')]
                    message = input("Enter your message: ")
                    print("📚 Loading document context...")
                    result = agent.chat_with_document_context(message, docs)
                    print(f"🤖 Gemini: {result}")
                else:
                    print("❌ Please provide document paths separated by commas")
            
            elif user_input.startswith('/summary'):
                parts = user_input.split(' ', 1)
                if len(parts) > 1:
                    sessions = [s.strip() for s in parts[1].split(',')]
                else:
                    sessions = None
                
                print("📝 Creating contextual summary...")
                summary = agent.create_contextual_summary(sessions)
                print(f"📋 Summary:\n{summary}")
            
            elif user_input.startswith('/export '):
                parts = user_input[8:].split()
                if parts:
                    session_name = parts[0]
                    format_type = parts[1] if len(parts) > 1 else "json"
                    print(f"💾 Exporting session '{session_name}' as {format_type}...")
                    agent.export_session_context(session_name, format_type=format_type)
                    print("✅ Export completed")
                else:
                    print("❌ Please provide a session name")
                
            elif user_input == '/history':
                stats = agent.get_stats()
                print(f"📊 Total interactions: {stats['total_interactions']}")
                print(f"🎯 Current session: {stats['current_session']}")
                print("📈 Session statistics:")
                for session_name, session_stats in stats['session_stats'].items():
                    print(f"   {session_name}: {session_stats['total_interactions']} interactions")
                    
            elif user_input == '/stats':
                stats = agent.get_stats()
                print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
                
            elif user_input.startswith('/'):
                print("❌ Unknown command. Available commands:")
                print("   /session <name>           - Create/switch session")
                print("   /list-sessions            - List all sessions")
                print("   /merge <s1,s2>           - Chat with merged context")
                print("   /doc-chat <doc1,doc2>    - Chat with document context")
                print("   /summary [sessions]      - Create contextual summary")
                print("   /export <session> [fmt]  - Export session")
                print("   /image, /analyze, /doc   - Other commands")
                print("   /history, /stats, /quit  - Info and exit")
                
            else:
                # Regular chat in current session
                print(f"🤖 Gemini [{current_session}]:", end=" ", flush=True)
                response = agent.chat(user_input)
                print(response)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main function with examples"""
    try:
        # Initialize agent
        agent = GeminiAgent()
        agent.set_system_instruction("You are a helpful AI assistant specialized in providing clear and concise answers.")
        
        print("🤖 Gemini AI Agent initialized successfully!")
        print(f"📊 Stats: {agent.get_stats()}")
        
        # Example usage
        print("\n" + "="*50)
        print("Example 1: Text Generation")
        response = agent.generate_text("Explain quantum computing in simple terms")
        print(f"Response: {response[:200]}...")
        
        print("\n" + "="*50)
        print("Example 2: Chat with context")
        response1 = agent.chat("What's the capital of France?")
        print(f"Response 1: {response1}")
        
        response2 = agent.chat("What's the population of that city?")
        print(f"Response 2: {response2}")
        
        # Start interactive mode
        print("\n" + "="*50)
        print("Starting interactive mode...")
        interactive_mode()
        
    except Exception as e:
        logger.error(f"Main error: {str(e)}")
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
