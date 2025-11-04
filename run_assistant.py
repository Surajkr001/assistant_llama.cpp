"""
Interactive Assistant Launcher
Allows user to choose between text and voice modes
"""

import logging
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from assistant_core import AssistantCore


def choose_mode():
    """Let user choose interaction mode"""
    print("\n" + "="*60)
    print("  AI Assistant - Mode Selection")
    print("="*60)
    print("\nSelect interaction mode:")
    print("  1. Text Chat")
    print("  2. Voice Mode")
    print("  3. Exit")
    
    while True:
        choice = input("\nYour choice (1-3): ").strip()
        
        if choice == '1':
            return 'text'
        elif choice == '2':
            return 'voice'
        elif choice == '3':
            return None
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def main():
    """Main function for interactive launcher"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('assistant.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Choose mode
        mode = choose_mode()
        
        if mode is None:
            print("\nExiting...")
            return
        
        # Load configuration
        config_path = Path(__file__).parent / "config.json"
        
        if not config_path.exists():
            logger.error("config.json not found!")
            print("\nError: config.json not found!")
            print("Please create a config.json file with your settings.")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Set mode
        config['assistant']['mode'] = mode
        
        print("\n" + "="*60)
        print(f"  AI Assistant - Initializing ({mode.upper()} mode)...")
        print("="*60)
        
        # Initialize assistant
        assistant = AssistantCore(config)
        
        if not assistant.initialize_all():
            logger.error("Failed to initialize assistant")
            print("\nFailed to initialize assistant. Check the logs for details.")
            return
        
        print("\n✓ Assistant initialized successfully!")
        
        # Start appropriate mode
        try:
            if mode == 'voice':
                if not assistant.stt:
                    print("\nWarning: Speech-to-Text not available!")
                    print("Voice mode requires STT. Falling back to text mode...")
                    assistant.start_text_chat()
                else:
                    assistant.start_voice_mode()
            else:
                assistant.start_text_chat()
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user...")
        
    except Exception as e:
        logger.error(f"Error in assistant launcher: {e}", exc_info=True)
        print(f"\nError: {e}")
    
    finally:
        # Cleanup
        try:
            assistant.shutdown()
            print("\nGoodbye!")
        except:
            pass


if __name__ == "__main__":
    main()
