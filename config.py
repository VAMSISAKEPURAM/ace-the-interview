"""
Centralized Configuration Module for Voice Chatbot.

All application parameters (paths, models, audio, logging, API keys)
are defined here to ensure separation of concerns and maintainability.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
CHAT_LOGS_DIR = DATA_DIR / "chat_logs"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for path in [DATA_DIR, AUDIO_DIR, CHAT_LOGS_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Groq & Hugging Face Credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Groq LLM Configurations
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "300"))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "15"))


# Auto-detect PyTorch Hardware Device (GPU / ZeroGPU or CPU)
try:
    import torch
    DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    DEFAULT_DEVICE = "cpu"

# Hugging Face Speech-to-Text (STT) Configurations
HF_STT_MODEL_NAME = os.getenv("HF_STT_MODEL_NAME", "openai/whisper-base")
STT_DEVICE = os.getenv("STT_DEVICE", DEFAULT_DEVICE)
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en")

# Hugging Face Text-to-Speech (TTS) Configurations
HF_TTS_MODEL_NAME = os.getenv("HF_TTS_MODEL_NAME", "facebook/mms-tts-eng")
TTS_DEVICE = os.getenv("TTS_DEVICE", DEFAULT_DEVICE)


# Audio Recording & Playback Parameters
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))  # 16kHz standard for Whisper/STT
CHANNELS = int(os.getenv("CHANNELS", "1"))           # Mono channel
DEFAULT_RECORD_DURATION = int(os.getenv("DEFAULT_RECORD_DURATION", "5")) # seconds
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "0.01"))
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "1.5")) # seconds of silence to stop recording

# Conversation Management
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

# Logging & Monitoring
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = LOGS_DIR / "app.log"
