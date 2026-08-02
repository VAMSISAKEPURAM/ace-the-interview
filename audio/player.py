"""
Speaker Audio Player Module.
Plays synthesized or recorded audio files through the speaker output.
"""

from pathlib import Path
from scipy.io import wavfile
from utils.logger import logger
from utils.helpers import validate_file_exists

class AudioPlayer:
    """
    Handles audio file playback with device cleanup.
    """
    def play(self, audio_path: Path) -> bool:
        """
        Play audio file from start to finish.
        
        Args:
            audio_path (Path): Path to WAV audio file.
            
        Returns:
            bool: True if playback completed successfully, False otherwise.
        """
        path = Path(audio_path)
        if not validate_file_exists(path):
            logger.error(f"Cannot play invalid or missing file: {path}")
            return False

        logger.info(f"Playing audio response: {path.name}")
        
        # Primary playback via sounddevice
        try:
            import sounddevice as sd
            sample_rate, audio_data = wavfile.read(str(path))
            sd.play(audio_data, sample_rate)
            sd.wait()  # Block until playback completes
            logger.info("Audio playback completed successfully.")
            return True
        except Exception as e:
            logger.warning(f"sounddevice playback failed ({e}), attempting fallback player.")

        # Fallback for Windows: winsound
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME)
            logger.info("Audio playback completed (winsound fallback).")
            return True
        except Exception as fallback_err:
            logger.error(f"Audio playback failed completely: {fallback_err}")
            return False
