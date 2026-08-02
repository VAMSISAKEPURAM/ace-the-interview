"""
Hugging Face Whisper Speech-to-Text Model Wrapper.
"""

from pathlib import Path
from typing import Optional
from config import HF_STT_MODEL_NAME, STT_DEVICE, STT_LANGUAGE
from utils.logger import logger
from utils.timer import Timer

class WhisperModel:
    """
    Wrapper for Hugging Face Speech Recognition models (e.g. openai/whisper-base).
    """
    def __init__(self, model_name: str = HF_STT_MODEL_NAME, device: str = STT_DEVICE):
        self.model_name = model_name
        self.device = device
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """
        Lazy loads the Hugging Face ASR pipeline.
        """
        logger.info(f"Loading Hugging Face STT model '{self.model_name}' on device '{self.device}'...")
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device
            )
            logger.info(f"Hugging Face STT model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Hugging Face STT model ({self.model_name}): {e}")
            self.pipeline = None

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe given audio file into text.
        
        Args:
            audio_path (Path): Path to WAV audio file.
            
        Returns:
            str: Transcribed text output.
        """
        path = str(audio_path)
        if not self.pipeline:
            logger.warning("STT Pipeline not initialized. Attempting re-initialization...")
            self._load_model()
            if not self.pipeline:
                logger.error("STT Model initialization failed. Returning empty transcription.")
                return ""

        with Timer("Hugging Face Speech Recognition"):
            try:
                import numpy as np
                from scipy.io import wavfile

                # Read audio file into numpy array using scipy to avoid ffmpeg system requirement
                sample_rate, audio_data = wavfile.read(path)
                
                # Convert 16-bit PCM integer data to float32 range [-1.0, 1.0]
                if audio_data.dtype == np.int16:
                    float_audio = audio_data.astype(np.float32) / 32768.0
                else:
                    float_audio = audio_data.astype(np.float32)

                inputs = {"raw": float_audio, "sampling_rate": sample_rate}
                result = self.pipeline(inputs, generate_kwargs={"language": STT_LANGUAGE})
                transcription = result.get("text", "").strip()
                logger.info(f"Recognized Speech: '{transcription}'")
                return transcription
            except Exception as e:
                logger.error(f"Error during audio transcription: {e}")
                return ""

