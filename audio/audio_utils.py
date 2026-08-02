"""
Audio Utilities module for audio signal manipulation, normalization, and silence detection.
"""

import numpy as np
from pathlib import Path
from scipy.io import wavfile
from utils.logger import logger

def normalize_audio_data(audio_data: np.ndarray) -> np.ndarray:
    """
    Normalizes floating point audio array to range [-1.0, 1.0] or int16 bounds.
    """
    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
    elif audio_data.dtype == np.int16:
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return (audio_data / max_val * 32767).astype(np.int16)
    return audio_data


def detect_silence(audio_chunk: np.ndarray, threshold: float = 0.01) -> bool:
    """
    Calculates Root Mean Square (RMS) energy to detect whether an audio chunk is silent.
    """
    if len(audio_chunk) == 0:
        return True
    
    # Calculate RMS energy
    if audio_chunk.dtype == np.int16:
        float_chunk = audio_chunk.astype(np.float32) / 32768.0
    else:
        float_chunk = audio_chunk.astype(np.float32)
        
    rms = np.sqrt(np.mean(float_chunk ** 2))
    return rms < threshold


def save_wav_file(file_path: Path, sample_rate: int, audio_data: np.ndarray):
    """
    Saves audio numpy array to a standard 16-bit PCM WAV file.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert float data to 16-bit PCM if required
    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
        audio_int16 = (audio_data * 32767).clip(-32768, 32767).astype(np.int16)
    else:
        audio_int16 = audio_data.astype(np.int16)
        
    wavfile.write(str(path), sample_rate, audio_int16)
    logger.debug(f"Saved audio file ({len(audio_int16)/sample_rate:.2f}s) to {path}")
