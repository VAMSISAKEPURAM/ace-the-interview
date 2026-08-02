"""
Microphone Audio Recorder Module.
Captures audio input from system microphone with configurable parameters.
"""

import time
import numpy as np
from pathlib import Path
from typing import Optional
from config import SAMPLE_RATE, CHANNELS, DEFAULT_RECORD_DURATION, SILENCE_THRESHOLD, SILENCE_DURATION
from audio.audio_utils import detect_silence, save_wav_file
from utils.logger import logger
from utils.helpers import get_timestamped_filename

class AudioRecorder:
    """
    Handles microphone audio recording using sounddevice or fallback simulation.
    """
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        silence_threshold: float = SILENCE_THRESHOLD,
        silence_duration: float = SILENCE_DURATION
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

    def record_fixed_duration(self, duration: float = DEFAULT_RECORD_DURATION, output_path: Optional[Path] = None) -> Path:
        """
        Record audio for a fixed number of seconds.
        """
        if output_path is None:
            output_path = get_timestamped_filename(prefix="user_speech", extension="wav")

        logger.info(f"Recording started ({duration} seconds)... Speak now.")
        
        try:
            import sounddevice as sd
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32"
            )
            sd.wait()  # Wait until recording is finished
            logger.info("Recording finished.")
            save_wav_file(output_path, self.sample_rate, recording.flatten())
            return output_path
        except Exception as e:
            logger.error(f"Error during microphone recording: {e}")
            # Generate silence fallback file if device error occurs
            empty_recording = np.zeros(int(duration * self.sample_rate), dtype=np.float32)
            save_wav_file(output_path, self.sample_rate, empty_recording)
            return output_path

    def record_with_vad(self, max_duration: float = 15.0, output_path: Optional[Path] = None) -> Path:
        """
        Record audio continuously until silence is detected or max_duration reached.
        """
        if output_path is None:
            output_path = get_timestamped_filename(prefix="user_speech", extension="wav")

        logger.info("Recording started (VAD enabled)... Speak now.")
        
        try:
            import sounddevice as sd
            chunks = []
            chunk_duration = 0.2  # 200ms chunks
            chunk_samples = int(chunk_duration * self.sample_rate)
            silent_chunks_limit = int(self.silence_duration / chunk_duration)
            silent_chunks_count = 0
            speech_started = False
            start_time = time.time()

            def callback(indata, frames, time_info, status):
                nonlocal silent_chunks_count, speech_started
                if status:
                    logger.warning(f"Audio stream status: {status}")
                
                audio_chunk = indata.copy().flatten()
                chunks.append(audio_chunk)
                
                is_silent = detect_silence(audio_chunk, self.silence_threshold)
                if not is_silent:
                    speech_started = True
                    silent_chunks_count = 0
                else:
                    if speech_started:
                        silent_chunks_count += 1

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                callback=callback,
                blocksize=chunk_samples
            ):
                while True:
                    time.sleep(0.1)
                    elapsed = time.time() - start_time
                    if speech_started and silent_chunks_count >= silent_chunks_limit:
                        logger.info("Silence detected. Stopping recording.")
                        break
                    if elapsed >= max_duration:
                        logger.info("Maximum record duration reached.")
                        break

            logger.info("Recording finished.")
            full_audio = np.concatenate(chunks) if chunks else np.zeros(self.sample_rate, dtype=np.float32)
            save_wav_file(output_path, self.sample_rate, full_audio)
            return output_path

        except Exception as e:
            logger.error(f"VAD recording failed ({e}), falling back to fixed duration.")
            return self.record_fixed_duration(duration=DEFAULT_RECORD_DURATION, output_path=output_path)
