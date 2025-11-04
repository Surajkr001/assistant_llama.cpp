"""
TextToSpeech - TTS engine wrapper supporting multiple backends
Converts text responses to speech output
"""

import logging
from typing import Dict, Optional
import threading
import queue

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 not installed. TTS features will be limited.")


class TextToSpeech:
    """
    Text-to-Speech engine with configurable voice settings
    Supports pyttsx3 (offline) with threading for non-blocking speech
    """
    
    def __init__(self, config: Dict):
        """
        Initialize TTS engine with configuration
        
        Args:
            config: Dictionary containing TTS configuration parameters
        """
        self.config = config
        self.engine = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.running = False
        
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """
        Initialize the TTS engine
        
        Returns:
            bool: True if initialized successfully, False otherwise
        """
        engine_type = self.config.get('engine', 'pyttsx3')
        
        if engine_type == 'pyttsx3':
            return self._initialize_pyttsx3()
        else:
            self.logger.error(f"Unsupported TTS engine: {engine_type}")
            return False
    
    def _initialize_pyttsx3(self) -> bool:
        """Initialize pyttsx3 TTS engine"""
        if not PYTTSX3_AVAILABLE:
            self.logger.error("pyttsx3 is not installed")
            return False
        
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            rate = self.config.get('rate', 175)
            volume = self.config.get('volume', 0.9)
            voice_id = self.config.get('voice_id', 0)
            
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Set voice if specified
            voices = self.engine.getProperty('voices')
            if 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
            
            self.logger.info("pyttsx3 TTS engine initialized successfully")
            
            # Start speech worker thread
            self.running = True
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            return False
    
    def _speech_worker(self):
        """Background worker thread for processing speech queue"""
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text is None:  # Shutdown signal
                    break
                    
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in speech worker: {e}")
                self.is_speaking = False
    
    def speak(self, text: str, blocking: bool = False):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not self.engine:
            self.logger.warning("TTS engine not initialized")
            return
        
        if not text or not text.strip():
            return
        
        try:
            if blocking:
                # Speak immediately in blocking mode
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            else:
                # Add to queue for async speaking
                self.speech_queue.put(text)
                
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
            self.is_speaking = False
    
    def stop(self):
        """Stop current speech"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                
                # Clear queue
                while not self.speech_queue.empty():
                    try:
                        self.speech_queue.get_nowait()
                    except queue.Empty:
                        break
                        
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
    
    def is_busy(self) -> bool:
        """
        Check if currently speaking
        
        Returns:
            bool: True if speaking, False otherwise
        """
        return self.is_speaking or not self.speech_queue.empty()
    
    def wait_until_done(self):
        """Wait until all queued speech is complete"""
        self.speech_queue.join()
    
    def set_rate(self, rate: int):
        """
        Set speech rate
        
        Args:
            rate: Speech rate (words per minute)
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.config['rate'] = rate
    
    def set_volume(self, volume: float):
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.config['volume'] = volume
    
    def list_voices(self) -> list:
        """
        Get list of available voices
        
        Returns:
            List of available voice objects
        """
        if self.engine:
            return self.engine.getProperty('voices')
        return []
    
    def set_voice(self, voice_id: int):
        """
        Set the voice by ID
        
        Args:
            voice_id: Index of the voice to use
        """
        if self.engine:
            voices = self.list_voices()
            if 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                self.config['voice_id'] = voice_id
                self.logger.info(f"Voice changed to: {voices[voice_id].name}")
    
    def shutdown(self):
        """Shutdown the TTS engine and cleanup resources"""
        self.running = False
        
        # Signal speech worker to stop
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_queue.put(None)
            self.speech_thread.join(timeout=2.0)
        
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
            self.engine = None
        
        self.logger.info("TTS engine shutdown")


# Example usage
if __name__ == "__main__":
    import json
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize and test TTS
    tts = TextToSpeech(config["tts"])
    
    if tts.initialize():
        print("TTS initialized successfully!")
        
        # List available voices
        voices = tts.list_voices()
        print(f"\nAvailable voices ({len(voices)}):")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name}")
        
        # Test speech
        print("\nTesting speech (non-blocking)...")
        tts.speak("Hello! I am your AI assistant. How can I help you today?")
        
        # Wait for speech to complete
        tts.wait_until_done()
        
        time.sleep(1)
        
        # Test blocking speech
        print("Testing speech (blocking)...")
        tts.speak("This is a blocking speech test.", blocking=True)
        
        print("Done!")
        
        # Cleanup
        tts.shutdown()
    else:
        print("Failed to initialize TTS")
