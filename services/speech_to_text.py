"""
Speech-to-Text (STT) Service Layer.
Decouples ASR implementation from application orchestrator.
"""

from pathlib import Path
from models.whisper_model import WhisperModel
from utils.logger import logger
from utils.helpers import validate_file_exists

class SpeechToTextService:
    """
    Service layer for Speech Recognition.
    """
    def __init__(self, stt_model: WhisperModel = None):
        self.stt_model = stt_model or WhisperModel()

    def process_audio(self, audio_file_path: Path) -> str:
        """
        Validates audio file and returns transcribed text.
        """
        if not validate_file_exists(audio_file_path):
            logger.warning("Invalid or empty audio file passed to STT Service.")
            return ""

        text = self.stt_model.transcribe(audio_file_path)
        if not text.strip():
            logger.info("No speech detected in audio file.")
            return ""
            
        return text
