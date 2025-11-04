"""
ChatInterface - Terminal-based text chat interface
Provides interactive text communication with the assistant
"""

import logging
from typing import Dict, Optional, Callable
import sys
from datetime import datetime


class ChatInterface:
    """
    Terminal-based chat interface for text interaction
    Handles user input, displays responses, and manages chat flow
    """
    
    def __init__(self, config: Dict):
        """
        Initialize chat interface with configuration
        
        Args:
            config: Dictionary containing assistant configuration
        """
        self.config = config
        self.assistant_name = config.get('name', 'Assistant')
        self.running = False
        self.message_callback: Optional[Callable] = None
        self.log_conversations = config.get('log_conversations', True)
        self.conversation_log = []
        
        self.logger = logging.getLogger(__name__)
    
    def set_message_callback(self, callback: Callable):
        """
        Set callback function for processing messages
        
        Args:
            callback: Function that takes user input and returns response
        """
        self.message_callback = callback
    
    def start(self):
        """Start the chat interface"""
        self.running = True
        self._print_welcome()
        self._chat_loop()
    
    def stop(self):
        """Stop the chat interface"""
        self.running = False
        self._print_goodbye()
    
    def _print_welcome(self):
        """Print welcome message"""
        print("\n" + "="*60)
        print(f"  {self.assistant_name} - AI Assistant")
        print("="*60)
        print("\nWelcome! I'm your AI assistant. I can help you with:")
        print("  • Answer questions and have conversations")
        print("  • Search the web for information")
        print("  • Control system applications")
        print("  • Read and write files")
        print("\nCommands:")
        print("  /help    - Show help")
        print("  /clear   - Clear conversation history")
        print("  /history - Show conversation history")
        print("  /quit    - Exit the assistant")
        print("\nType your message and press Enter to chat.")
        print("="*60 + "\n")
    
    def _print_goodbye(self):
        """Print goodbye message"""
        print("\n" + "="*60)
        print(f"  Thank you for using {self.assistant_name}!")
        print("="*60 + "\n")
    
    def _chat_loop(self):
        """Main chat loop"""
        while self.running:
            try:
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Process message through callback
                if self.message_callback:
                    print(f"\n{self.assistant_name}: ", end='', flush=True)
                    
                    response = self.message_callback(user_input)
                    print(response)
                    
                    # Log conversation
                    if self.log_conversations:
                        self._log_message("user", user_input)
                        self._log_message("assistant", response)
                else:
                    print(f"\n{self.assistant_name}: Error - No message handler configured")
                
                print()  # Empty line for spacing
                
            except KeyboardInterrupt:
                print("\n")
                self.stop()
                break
            except EOFError:
                self.stop()
                break
            except Exception as e:
                self.logger.error(f"Error in chat loop: {e}")
                print(f"\nError: {e}\n")
    
    def _get_user_input(self) -> str:
        """
        Get input from user
        
        Returns:
            str: User input text
        """
        try:
            user_input = input("You: ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            self.logger.error(f"Error getting user input: {e}")
            return ""
    
    def _handle_command(self, command: str):
        """
        Handle chat commands
        
        Args:
            command: Command string starting with /
        """
        cmd = command.lower().split()[0]
        
        if cmd == '/help':
            self._show_help()
        elif cmd == '/clear':
            self._clear_history()
        elif cmd == '/history':
            self._show_history()
        elif cmd == '/quit' or cmd == '/exit':
            self.stop()
        else:
            print(f"\nUnknown command: {cmd}")
            print("Type /help for available commands\n")
    
    def _show_help(self):
        """Show help information"""
        print("\n" + "="*60)
        print("  Available Commands")
        print("="*60)
        print("\n/help    - Show this help message")
        print("/clear   - Clear conversation history")
        print("/history - Show conversation history")
        print("/quit    - Exit the assistant")
        print("\nYou can also ask me to:")
        print("  • Search the web: 'Search for Python tutorials'")
        print("  • Open apps: 'Open notepad'")
        print("  • Get system info: 'What is my CPU usage?'")
        print("  • Read files: 'Read the file at C:\\...'")
        print("="*60 + "\n")
    
    def _clear_history(self):
        """Clear conversation history"""
        self.conversation_log.clear()
        print(f"\n{self.assistant_name}: Conversation history cleared.\n")
    
    def _show_history(self):
        """Show conversation history"""
        if not self.conversation_log:
            print(f"\n{self.assistant_name}: No conversation history yet.\n")
            return
        
        print("\n" + "="*60)
        print("  Conversation History")
        print("="*60 + "\n")
        
        for entry in self.conversation_log:
            timestamp = entry['timestamp']
            role = entry['role'].capitalize()
            message = entry['message']
            
            print(f"[{timestamp}] {role}: {message}\n")
        
        print("="*60 + "\n")
    
    def _log_message(self, role: str, message: str):
        """
        Log a message to conversation history
        
        Args:
            role: Role (user or assistant)
            message: Message text
        """
        self.conversation_log.append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'role': role,
            'message': message
        })
    
    def display_message(self, message: str, role: str = "assistant"):
        """
        Display a message in the chat interface
        
        Args:
            message: Message text
            role: Role (user or assistant)
        """
        if role == "assistant":
            print(f"\n{self.assistant_name}: {message}\n")
        else:
            print(f"\n{role.capitalize()}: {message}\n")
        
        if self.log_conversations:
            self._log_message(role, message)
    
    def get_conversation_log(self) -> list:
        """
        Get the conversation log
        
        Returns:
            List of conversation entries
        """
        return self.conversation_log.copy()
    
    def save_conversation(self, filepath: str) -> bool:
        """
        Save conversation to file
        
        Args:
            filepath: Path to save file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write(f"  {self.assistant_name} - Conversation Log\n")
                f.write("="*60 + "\n\n")
                
                for entry in self.conversation_log:
                    timestamp = entry['timestamp']
                    role = entry['role'].capitalize()
                    message = entry['message']
                    
                    f.write(f"[{timestamp}] {role}:\n{message}\n\n")
            
            self.logger.info(f"Conversation saved to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize chat interface
    chat = ChatInterface(config["assistant"])
    
    # Set up a simple echo callback for testing
    def echo_callback(message: str) -> str:
        return f"You said: {message}"
    
    chat.set_message_callback(echo_callback)
    
    # Start chat
    chat.start()
