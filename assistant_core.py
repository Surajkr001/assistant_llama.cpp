"""
AssistantCore - Central orchestrator for AI assistant
Coordinates all modules and handles request routing
"""

import logging
import asyncio
from typing import Dict, Optional
import re
import json


class AssistantCore:
    """
    Central orchestration class that coordinates all assistant modules
    Handles request routing, intent detection, and response generation
    """
    
    def __init__(self, config: Dict):
        """
        Initialize assistant core with configuration
        
        Args:
            config: Complete configuration dictionary
        """
        self.config = config
        self.llm = None
        self.tts = None
        self.stt = None
        self.web = None
        self.system = None
        self.chat = None
        
        self.logger = logging.getLogger(__name__)
        self.initialized = False
    
    def initialize_all(self) -> bool:
        """
        Initialize all assistant modules
        
        Returns:
            bool: True if all modules initialized successfully
        """
        try:
            from llama_model import LlamaModel
            from tts_engine import TextToSpeech
            from stt_engine import SpeechToText
            from web_tools import WebTools
            from system_control import SystemControl
            from chat_interface import ChatInterface
            
            self.logger.info("Initializing assistant modules...")
            
            # Initialize LLM
            self.logger.info("Loading LLM model...")
            self.llm = LlamaModel(self.config['llm'])
            if not self.llm.load_model():
                self.logger.error("Failed to load LLM model")
                return False
            
            # Initialize TTS
            self.logger.info("Initializing TTS engine...")
            self.tts = TextToSpeech(self.config['tts'])
            if not self.tts.initialize():
                self.logger.warning("TTS initialization failed, continuing without TTS")
            
            # Initialize STT
            self.logger.info("Initializing STT engine...")
            self.stt = SpeechToText(self.config['stt'])
            if not self.stt.initialize():
                self.logger.warning("STT initialization failed, continuing without STT")
            
            # Initialize Web Tools
            self.logger.info("Initializing web tools...")
            self.web = WebTools(self.config['web'])
            
            # Initialize System Control
            self.logger.info("Initializing system control...")
            self.system = SystemControl(self.config['system'])
            
            # Initialize Chat Interface
            self.logger.info("Initializing chat interface...")
            self.chat = ChatInterface(self.config['assistant'])
            self.chat.set_message_callback(self.process_message)
            
            self.initialized = True
            self.logger.info("All modules initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            return False
    
    def process_message(self, user_input: str) -> str:
        """
        Process user message and generate response
        
        Args:
            user_input: User input text
            
        Returns:
            str: Assistant response
        """
        if not self.initialized:
            return "Error: Assistant not initialized"
        
        try:
            # Detect intent
            intent = self._detect_intent(user_input)
            
            # Route to appropriate handler
            if intent == 'web_search':
                return self._handle_web_search(user_input)
            elif intent == 'system_control':
                return self._handle_system_control(user_input)
            elif intent == 'file_operation':
                return self._handle_file_operation(user_input)
            elif intent == 'system_info':
                return self._handle_system_info(user_input)
            else:
                # Default: Generate LLM response
                return self._handle_conversation(user_input)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return f"I encountered an error: {str(e)}"
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect user intent from input text
        
        Args:
            text: User input text
            
        Returns:
            str: Detected intent
        """
        text_lower = text.lower()
        
        # Web search patterns
        search_patterns = [
            r'search (for|about|up)',
            r'look (up|for)',
            r'find (information|info|out) (about|on)',
            r'what is',
            r'who is',
            r'where is',
            r'how to'
        ]
        
        for pattern in search_patterns:
            if re.search(pattern, text_lower):
                return 'web_search'
        
        # System control patterns
        control_patterns = [
            r'open (application|app|program)',
            r'launch',
            r'start (application|app|program)',
            r'run (application|app|program)',
            r'open (notepad|calculator|explorer|chrome|firefox)'
        ]
        
        for pattern in control_patterns:
            if re.search(pattern, text_lower):
                return 'system_control'
        
        # File operation patterns
        file_patterns = [
            r'read (the |)file',
            r'write (to |)file',
            r'create (a |)file',
            r'list (files|directory)',
            r'show (files|directory)'
        ]
        
        for pattern in file_patterns:
            if re.search(pattern, text_lower):
                return 'file_operation'
        
        # System info patterns
        info_patterns = [
            r'system (info|information)',
            r'cpu usage',
            r'memory usage',
            r'disk space',
            r'what are my system specs'
        ]
        
        for pattern in info_patterns:
            if re.search(pattern, text_lower):
                return 'system_info'
        
        return 'conversation'
    
    def _handle_web_search(self, query: str) -> str:
        """Handle web search requests"""
        self.logger.info(f"Handling web search: {query}")
        
        # Extract search query
        search_query = query
        for prefix in ['search for', 'search about', 'look up', 'find information about']:
            if prefix in query.lower():
                search_query = query.lower().split(prefix, 1)[1].strip()
                break
        
        # Perform search
        results = self.web.search_and_summarize(search_query)
        
        # Generate response with LLM
        prompt = f"Based on these search results, provide a helpful answer:\n\n{results}\n\nUser question: {query}"
        llm_response = self.llm.generate_response(prompt, use_history=False)
        
        return llm_response
    
    def _handle_system_control(self, command: str) -> str:
        """Handle system control requests"""
        self.logger.info(f"Handling system control: {command}")
        
        # Extract application name
        app_name = None
        for app in self.config['system']['allowed_commands']:
            if app.lower() in command.lower():
                app_name = app
                break
        
        if app_name:
            success = self.system.open_application(app_name)
            if success:
                return f"I've opened {app_name} for you."
            else:
                return f"Sorry, I couldn't open {app_name}. Please check if the application is installed."
        else:
            return "I'm not sure which application you want to open. Please specify one of the allowed applications."
    
    def _handle_file_operation(self, command: str) -> str:
        """Handle file operation requests"""
        self.logger.info(f"Handling file operation: {command}")
        
        command_lower = command.lower()
        
        # Read file
        if 'read' in command_lower:
            # Extract file path (simple pattern matching)
            import re
            path_match = re.search(r'[A-Za-z]:\\[^\s]+|/[^\s]+', command)
            if path_match:
                filepath = path_match.group(0)
                content = self.system.read_file(filepath)
                if content:
                    return f"File contents:\n\n{content[:500]}..." if len(content) > 500 else f"File contents:\n\n{content}"
                else:
                    return "Sorry, I couldn't read that file. Please check the path and permissions."
            else:
                return "Please specify the file path you want to read."
        
        # List directory
        elif 'list' in command_lower or 'show' in command_lower:
            path_match = re.search(r'[A-Za-z]:\\[^\s]+|/[^\s]+', command)
            if path_match:
                dirpath = path_match.group(0)
                items = self.system.list_directory(dirpath)
                if items:
                    return f"Directory contents:\n" + "\n".join(f"  - {item}" for item in items[:20])
                else:
                    return "Sorry, I couldn't list that directory."
            else:
                return "Please specify the directory path."
        
        return "I can help you read files or list directories. Please provide more details."
    
    def _handle_system_info(self, query: str) -> str:
        """Handle system information requests"""
        self.logger.info(f"Handling system info: {query}")
        
        info = self.system.get_system_info()
        
        info_text = "System Information:\n"
        for key, value in info.items():
            info_text += f"  {key.replace('_', ' ').title()}: {value}\n"
        
        # Generate natural response with LLM
        prompt = f"Based on this system information, provide a natural response to the user:\n\n{info_text}\n\nUser question: {query}"
        response = self.llm.generate_response(prompt, use_history=False)
        
        return response
    
    def _handle_conversation(self, message: str) -> str:
        """Handle general conversation"""
        self.logger.info(f"Handling conversation: {message}")
        
        # Generate response with LLM
        response = self.llm.generate_response(message, use_history=True)
        return response
    
    def process_voice_input(self) -> Optional[str]:
        """
        Process voice input and return transcribed text
        
        Returns:
            str: Transcribed text, or None if failed
        """
        if not self.stt:
            self.logger.warning("STT not initialized")
            return None
        
        return self.stt.listen(timeout=10, phrase_time_limit=15)
    
    def speak_response(self, text: str, blocking: bool = False):
        """
        Speak response using TTS
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if self.tts:
            self.tts.speak(text, blocking=blocking)
    
    def start_text_chat(self):
        """Start text-based chat interface"""
        if self.chat:
            self.chat.start()
    
    def start_voice_mode(self):
        """Start voice interaction mode"""
        print("\n" + "="*60)
        print("  Voice Mode Activated")
        print("="*60)
        print("\nListening for your voice commands...")
        print("Press Ctrl+C to exit voice mode\n")
        
        try:
            while True:
                # Listen for input
                print("Listening...")
                text = self.process_voice_input()
                
                if text:
                    print(f"You said: {text}\n")
                    
                    # Process and respond
                    response = self.process_message(text)
                    print(f"Assistant: {response}\n")
                    
                    # Speak response
                    self.speak_response(response, blocking=True)
                else:
                    print("Sorry, I didn't catch that.\n")
                
        except KeyboardInterrupt:
            print("\n\nExiting voice mode...")
    
    def shutdown(self):
        """Shutdown all modules and cleanup"""
        self.logger.info("Shutting down assistant...")
        
        if self.llm:
            self.llm.unload_model()
        
        if self.tts:
            self.tts.shutdown()
        
        if self.stt:
            self.stt.shutdown()
        
        if self.web:
            self.web.shutdown()
        
        if self.system:
            self.system.shutdown()
        
        self.logger.info("Assistant shutdown complete")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize assistant
    assistant = AssistantCore(config)
    
    if assistant.initialize_all():
        print("\nAssistant initialized successfully!")
        
        # Start text chat
        assistant.start_text_chat()
        
        # Shutdown
        assistant.shutdown()
    else:
        print("\nFailed to initialize assistant")
