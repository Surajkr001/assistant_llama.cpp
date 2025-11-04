"""
SpeechToText - STT engine wrapper supporting multiple backends
Converts speech input to text for processing
"""

import logging
from typing import Dict, Optional
import threading
import time

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logging.warning("speech_recognition not installed. STT features will be limited.")


class SpeechToText:
    """
    Speech-to-Text engine with configurable recognition settings
    Supports Google Speech Recognition, Whisper, and Sphinx
    """
    
    def __init__(self, config: Dict):
        """
        Initialize STT engine with configuration
        
        Args:
            config: Dictionary containing STT configuration parameters
        """
        self.config = config
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """
        Initialize the STT engine
        
        Returns:
            bool: True if initialized successfully, False otherwise
        """
        if not SR_AVAILABLE:
            self.logger.error("speech_recognition library is not installed")
            return False
        
        try:
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer properties
            self.recognizer.energy_threshold = self.config.get('energy_threshold', 4000)
            self.recognizer.pause_threshold = self.config.get('pause_threshold', 1.0)
            self.recognizer.dynamic_energy_threshold = True
            
            # Initialize microphone
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            with self.microphone as source:
                self.logger.info("Calibrating for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("STT engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize STT: {e}")
            return False
    
    def listen(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """
        Listen for speech input and convert to text
        
        Args:
            timeout: Maximum time to wait for speech to start (seconds)
            phrase_time_limit: Maximum time for the phrase (seconds)
            
        Returns:
            str: Recognized text, or None if recognition failed
        """
        if not self.recognizer or not self.microphone:
            self.logger.error("STT engine not initialized")
            return None
        
        try:
            self.is_listening = True
            
            with self.microphone as source:
                self.logger.info("Listening...")
                
                # Listen for audio input
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            self.is_listening = False
            self.logger.info("Processing speech...")
            
            # Recognize speech using configured engine
            text = self._recognize_speech(audio)
            
            if text:
                self.logger.info(f"Recognized: {text}")
            
            return text
            
        except sr.WaitTimeoutError:
            self.logger.warning("Listening timed out")
            self.is_listening = False
            return None
        except Exception as e:
            self.logger.error(f"Error during listening: {e}")
            self.is_listening = False
            return None
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """
        Recognize speech from audio using configured engine
        
        Args:
            audio: Audio data from microphone
            
        Returns:
            str: Recognized text, or None if failed
        """
        engine = self.config.get('engine', 'whisper')
        language = self.config.get('language', 'en')
        
        try:
            if engine == 'whisper':
                # Use OpenAI Whisper (local or API)
                model = self.config.get('model', 'base')
                return self.recognizer.recognize_whisper(audio, model=model, language=language)
                
            elif engine == 'google':
                # Use Google Speech Recognition (requires internet)
                return self.recognizer.recognize_google(audio, language=language)
                
            elif engine == 'sphinx':
                # Use CMU Sphinx (offline, less accurate)
                return self.recognizer.recognize_sphinx(audio)
                
            else:
                # Default to Google
                return self.recognizer.recognize_google(audio, language=language)
                
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error recognizing speech: {e}")
            return None
    
    def listen_background(self, callback, phrase_time_limit: Optional[float] = None):
        """
        Start listening in background mode with callback
        
        Args:
            callback: Function to call with recognized text
            phrase_time_limit: Maximum time for each phrase
        """
        if not self.recognizer or not self.microphone:
            self.logger.error("STT engine not initialized")
            return None
        
        def audio_callback(recognizer, audio):
            """Process audio in background"""
            try:
                text = self._recognize_speech(audio)
                if text and callback:
                    callback(text)
            except Exception as e:
                self.logger.error(f"Error in background recognition: {e}")
        
        # Start background listening
        stop_listening = self.recognizer.listen_in_background(
            self.microphone,
            audio_callback,
            phrase_time_limit=phrase_time_limit
        )
        
        self.logger.info("Background listening started")
        return stop_listening
    
    def is_busy(self) -> bool:
        """
        Check if currently listening
        
        Returns:
            bool: True if listening, False otherwise
        """
        return self.is_listening
    
    def test_microphone(self) -> bool:
        """
        Test if microphone is working
        
        Returns:
            bool: True if microphone is accessible
        """
        try:
            with self.microphone as source:
                self.logger.info("Microphone test: Recording for 2 seconds...")
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=2)
                self.logger.info("Microphone test: Success!")
                return True
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def list_microphones(self) -> list:
        """
        Get list of available microphone devices
        
        Returns:
            List of microphone device names
        """
        if SR_AVAILABLE:
            return sr.Microphone.list_microphone_names()
        return []
    
    def set_microphone(self, device_index: int) -> bool:
        """
        Set the microphone device
        
        Args:
            device_index: Index of the microphone device
            
        Returns:
            bool: True if successful
        """
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            
            # Re-calibrate for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info(f"Microphone changed to device {device_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set microphone: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the STT engine"""
        self.is_listening = False
        self.recognizer = None
        self.microphone = None
        self.logger.info("STT engine shutdown")


# Example usage
if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize and test STT
    stt = SpeechToText(config["stt"])
    
    if stt.initialize():
        print("STT initialized successfully!")
        
        # List available microphones
        mics = stt.list_microphones()
        print(f"\nAvailable microphones ({len(mics)}):")
        for i, mic in enumerate(mics):
            print(f"  {i}: {mic}")
        
        # Test listening
        print("\n" + "="*50)
        print("Say something! (5 second timeout)")
        print("="*50)
        
        text = stt.listen(timeout=5, phrase_time_limit=10)
        
        if text:
            print(f"\nYou said: {text}")
        else:
            print("\nNo speech detected or recognition failed")
        
        # Cleanup
        stt.shutdown()
    else:
        print("Failed to initialize STT")
