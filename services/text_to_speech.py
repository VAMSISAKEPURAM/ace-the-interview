"""
Text-to-Speech (TTS) Service Layer.
Decouples speech synthesis implementation from application orchestrator.
"""

from pathlib import Path
from typing import Optional
from models.tts_model import TTSModel
from utils.logger import logger
from utils.helpers import validate_file_exists

class TextToSpeechService:
    """
    Service layer orchestrating speech synthesis.
    """
    def __init__(self, tts_model: TTSModel = None):
        self.tts_model = tts_model or TTSModel()

    def generate_speech(self, text: str, output_path: Optional[Path] = None) -> Path:
        """
        Converts text string into spoken audio WAV file.
        """
        if not text or not text.strip():
            logger.warning("Empty text string provided to TextToSpeechService.")
            text = "I didn't catch that."

        audio_file = self.tts_model.synthesize(text=text, output_path=output_path)
        
        if not validate_file_exists(audio_file):
            logger.error("TTS Service failed to produce a valid audio file.")
            
        return audio_file
