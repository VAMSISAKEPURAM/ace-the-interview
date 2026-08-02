"""
Hugging Face Text-to-Speech (TTS) Model Wrapper.
"""

from pathlib import Path
from typing import Optional
from config import HF_TTS_MODEL_NAME, TTS_DEVICE, SAMPLE_RATE
from utils.logger import logger
from utils.timer import Timer
from utils.helpers import get_timestamped_filename
from audio.audio_utils import save_wav_file

class TTSModel:
    """
    Wrapper for Hugging Face Text-to-Speech synthesis (e.g. facebook/mms-tts-eng).
    """
    def __init__(self, model_name: str = HF_TTS_MODEL_NAME, device: str = TTS_DEVICE):
        self.model_name = model_name
        self.device = device
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """
        Loads the Hugging Face TTS pipeline or sets fallback mode.
        """
        logger.info(f"Loading Hugging Face TTS model '{self.model_name}' on device '{self.device}'...")
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "text-to-speech",
                model=self.model_name,
                device=self.device
            )
            logger.info(f"Hugging Face TTS model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load Hugging Face pipeline for '{self.model_name}': {e}. Using fallback TTS engine.")
            self.pipeline = None

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> Path:
        """
        Synthesize input text into spoken audio saved to file.
        
        Args:
            text (str): Spoken input string.
            output_path (Optional[Path]): Destination audio path.
            
        Returns:
            Path: File path to generated WAV audio file.
        """
        if output_path is None:
            output_path = get_timestamped_filename(prefix="assistant_speech", extension="wav")

        if not text.strip():
            logger.warning("Empty text passed for TTS synthesis.")
            text = "I am listening."

        with Timer("Hugging Face Speech Synthesis"):
            # Hugging Face pipeline synthesis
            if self.pipeline:
                try:
                    logger.info(f"Synthesizing speech via HF model '{self.model_name}'...")
                    result = self.pipeline(text)
                    audio_data = result["audio"].flatten()
                    sampling_rate = result.get("sampling_rate", SAMPLE_RATE)
                    save_wav_file(output_path, sampling_rate, audio_data)
                    return output_path
                except Exception as e:
                    logger.error(f"Hugging Face TTS synthesis failed ({e}). Falling back.")

            # Fallback 1: pyttsx3 offline TTS engine
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.save_to_file(text, str(output_path))
                engine.runAndWait()
                logger.info("Synthesized speech using pyttsx3 fallback.")
                return output_path
            except Exception as pyttsx_err:
                logger.warning(f"pyttsx3 fallback failed ({pyttsx_err}). Trying gTTS...")

            # Fallback 2: gTTS (google text-to-speech)
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en')
                tts.save(str(output_path))
                logger.info("Synthesized speech using gTTS fallback.")
                return output_path
            except Exception as gtts_err:
                logger.error(f"All TTS synthesis engines failed: {gtts_err}")
                return output_path
