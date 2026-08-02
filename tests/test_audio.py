"""
Unit tests for audio utilities and signal normalization.
"""

import unittest
import numpy as np
from config import AUDIO_DIR
from audio.audio_utils import normalize_audio_data, detect_silence, save_wav_file

class TestAudioUtils(unittest.TestCase):
    def test_normalize_audio_data(self):
        float_audio = np.array([0.5, -1.0, 2.0], dtype=np.float32)
        normalized = normalize_audio_data(float_audio)
        self.assertEqual(np.max(np.abs(normalized)), 1.0)

    def test_detect_silence(self):
        silent_chunk = np.zeros(1000, dtype=np.float32)
        self.assertTrue(detect_silence(silent_chunk, threshold=0.01))

        loud_chunk = np.ones(1000, dtype=np.float32) * 0.5
        self.assertFalse(detect_silence(loud_chunk, threshold=0.01))

    def test_save_wav_file(self):
        wav_path = AUDIO_DIR / "dummy_signal_test.wav"
        audio_data = np.zeros(16000, dtype=np.float32)
        save_wav_file(wav_path, sample_rate=16000, audio_data=audio_data)
        self.assertTrue(wav_path.exists())
        self.assertGreater(wav_path.stat().st_size, 0)
        wav_path.unlink()

if __name__ == "__main__":
    unittest.main()

