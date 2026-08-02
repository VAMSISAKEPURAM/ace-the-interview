"""
General Helper Utilities.
"""

import os
from datetime import datetime
from pathlib import Path
from config import AUDIO_DIR, CHAT_LOGS_DIR, GROQ_API_KEY
from utils.logger import logger

def get_timestamped_filename(prefix: str = "audio", extension: str = "wav") -> Path:
    """
    Generates a unique timestamped file path in the audio directory.
    
    Example: data/audio/user_input_20260802_123045.wav
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
    filename = f"{prefix}_{timestamp}.{extension.lstrip('.')}"
    return AUDIO_DIR / filename


def validate_file_exists(file_path: Path) -> bool:
    """
    Validates if a file exists and is not empty.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {path}")
        return False
    if path.stat().st_size == 0:
        logger.warning(f"File is empty (0 bytes): {path}")
        return False
    return True


def safe_delete_file(file_path: Path):
    """
    Safely deletes a file if it exists.
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.debug(f"Deleted file: {path}")
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")


def validate_environment() -> dict:
    """
    Checks environment configurations and returns status warnings/errors.
    """
    status = {"groq_key_present": bool(GROQ_API_KEY.strip() and not GROQ_API_KEY.startswith("your_"))}
    if not status["groq_key_present"]:
        logger.warning("GROQ_API_KEY is not set. Groq LLM calls will fail until provided in environment.")
    return status
