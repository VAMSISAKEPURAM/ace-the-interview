"""
Groq Cloud LLM Model Wrapper.
High-speed inference API for LLaMA 3 models.
"""

from typing import List, Dict
from config import GROQ_API_KEY, GROQ_MODEL_NAME, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT
from utils.logger import logger
from utils.timer import Timer

class GroqModel:
    """
    Wrapper for interacting with Groq Cloud API.
    """
    def __init__(
        self,
        api_key: str = GROQ_API_KEY,
        model_name: str = GROQ_MODEL_NAME,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
        timeout: int = LLM_TIMEOUT
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Groq API client."""
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("Groq API key missing or default placeholder. Groq calls will fail until configured.")
            return

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key, timeout=self.timeout)
            logger.info(f"Groq Client initialized for model '{self.model_name}'.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Send message history to Groq Chat Completion API.
        
        Args:
            messages (List[Dict]): List of role/content message dicts.
            
        Returns:
            str: Assistant text response.
        """
        if not self.client:
            self._init_client()
            if not self.client:
                logger.error("Groq Client not available.")
                return "I apologize, but my language model service is currently offline because the Groq API key is missing or invalid."

        with Timer("Groq LLM Response Generation"):
            try:
                logger.info(f"Sending request to Groq API ({self.model_name})...")
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                assistant_text = response.choices[0].message.content.strip()
                logger.info(f"Groq Response: '{assistant_text}'")
                return assistant_text
            except Exception as e:
                logger.error(f"Groq API Call failed: {e}")
                return "I'm having trouble processing that request right now. Could you please try speaking again?"
