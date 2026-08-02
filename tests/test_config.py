"""
Unit tests for configuration and helper utilities.
"""

import unittest
from pathlib import Path
from config import BASE_DIR, DATA_DIR, AUDIO_DIR
from utils.helpers import get_timestamped_filename, validate_file_exists, safe_delete_file

class TestConfigAndHelpers(unittest.TestCase):
    def test_paths_exist(self):
        self.assertTrue(DATA_DIR.exists())
        self.assertTrue(AUDIO_DIR.exists())

    def test_timestamped_filename(self):
        filename = get_timestamped_filename(prefix="test_audio", extension="wav")
        self.setIsInstance = isinstance(filename, Path)
        self.assertTrue(filename.name.startswith("test_audio"))
        self.assertTrue(filename.name.endswith(".wav"))

    def test_file_validation_and_cleanup(self):
        test_file = AUDIO_DIR / "dummy_test_file.txt"
        self.assertFalse(validate_file_exists(test_file))
        
        test_file.write_text("Hello World")
        self.assertTrue(validate_file_exists(test_file))
        
        safe_delete_file(test_file)
        self.assertFalse(test_file.exists())

if __name__ == "__main__":
    unittest.main()

