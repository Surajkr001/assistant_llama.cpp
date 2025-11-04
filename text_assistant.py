"""
Text Assistant - Text-based chat interface demo
Example script for text-only interaction with the AI assistant
"""

import logging
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from assistant_core import AssistantCore


def main():
    """Main function for text assistant"""
    
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
        # Load configuration
        config_path = Path(__file__).parent / "config.json"
        
        if not config_path.exists():
            logger.error("config.json not found!")
            print("\nError: config.json not found!")
            print("Please create a config.json file with your settings.")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Set mode to text
        config['assistant']['mode'] = 'text'
        
        print("\n" + "="*60)
        print("  AI Text Assistant - Initializing...")
        print("="*60)
        
        # Initialize assistant
        assistant = AssistantCore(config)
        
        if not assistant.initialize_all():
            logger.error("Failed to initialize assistant")
            print("\nFailed to initialize assistant. Check the logs for details.")
            return
        
        print("\n✓ Assistant initialized successfully!")
        
        # Start text chat interface
        try:
            assistant.start_text_chat()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user...")
        
    except Exception as e:
        logger.error(f"Error in text assistant: {e}", exc_info=True)
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
