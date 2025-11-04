"""
LlamaModel - Local LLM integration using llama-cpp-python
Handles all LLM inference with GPU acceleration
"""

import logging
from typing import List, Dict, Optional
import json

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logging.warning("llama-cpp-python not installed. LLM features will be limited.")


class LlamaModel:
    """
    Manages local LLM inference using llama.cpp bindings
    Supports GPU acceleration and conversation context
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Llama model with configuration
        
        Args:
            config: Dictionary containing llm configuration parameters
        """
        self.config = config
        self.model = None
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = """You are Jarvis, a helpful AI assistant with access to the internet and system controls. 
You can help with questions, search the web for information, and control system applications when requested.
Be concise, helpful, and friendly in your responses."""
        
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> bool:
        """
        Load the LLM model with GPU acceleration
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not LLAMA_AVAILABLE:
            self.logger.error("llama-cpp-python is not installed")
            return False
            
        try:
            self.logger.info(f"Loading model from {self.config['model_path']}")
            
            self.model = Llama(
                model_path=self.config['model_path'],
                n_gpu_layers=self.config.get('n_gpu_layers', 35),
                n_ctx=self.config.get('n_ctx', 4096),
                n_threads=self.config.get('n_threads', 8),
                verbose=self.config.get('verbose', False)
            )
            
            self.logger.info("Model loaded successfully with GPU acceleration")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
    
    def generate_response(self, prompt: str, use_history: bool = True) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User input text
            use_history: Whether to include conversation history
            
        Returns:
            str: Generated response from the LLM
        """
        if not self.model:
            return "Error: Model not loaded. Please load the model first."
        
        try:
            # Build the full prompt with system message and history
            full_prompt = self._build_prompt(prompt, use_history)
            
            # Generate response
            response = self.model(
                full_prompt,
                max_tokens=self.config.get('max_tokens', 512),
                temperature=self.config.get('temperature', 0.7),
                top_p=self.config.get('top_p', 0.95),
                repeat_penalty=self.config.get('repeat_penalty', 1.1),
                stop=["User:", "Human:", "\n\n\n"]
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Update conversation history
            if use_history:
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": generated_text})
                
                # Limit history size
                max_history = 10
                if len(self.conversation_history) > max_history * 2:
                    self.conversation_history = self.conversation_history[-(max_history * 2):]
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _build_prompt(self, user_input: str, use_history: bool) -> str:
        """
        Build the complete prompt with system message and history
        
        Args:
            user_input: Current user input
            use_history: Whether to include conversation history
            
        Returns:
            str: Complete formatted prompt
        """
        prompt_parts = [f"System: {self.system_prompt}\n"]
        
        if use_history and self.conversation_history:
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg['content']}\n")
        
        prompt_parts.append(f"User: {user_input}\nAssistant:")
        
        return "\n".join(prompt_parts)
    
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def set_system_prompt(self, prompt: str):
        """
        Update the system prompt
        
        Args:
            prompt: New system prompt
        """
        self.system_prompt = prompt
        self.logger.info("System prompt updated")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def unload_model(self):
        """Unload the model and free resources"""
        if self.model:
            del self.model
            self.model = None
            self.logger.info("Model unloaded")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize and test the model
    llm = LlamaModel(config["llm"])
    
    if llm.load_model():
        print("Model loaded successfully!")
        
        # Test generation
        response = llm.generate_response("Hello! What can you help me with?")
        print(f"Response: {response}")
        
        # Clean up
        llm.unload_model()
    else:
        print("Failed to load model")
