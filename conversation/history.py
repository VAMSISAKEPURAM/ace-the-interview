"""
Conversation History Module.
Maintains an ordered list of system, user, and assistant messages.
"""

from typing import List, Dict
from conversation.prompt import DEFAULT_SYSTEM_PROMPT
from utils.logger import logger

class ConversationHistory:
    """
    Manages in-memory message queue for OpenAI format chat completion.
    """
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self._system_prompt = system_prompt
        self.messages: List[Dict[str, str]] = []
        self._reset()

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str):
        self._system_prompt = value
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = value
        elif not self.messages:
            self.messages = [{"role": "system", "content": value}]

    def _reset(self):
        """Reset conversation back to system prompt."""
        self.messages = [{"role": "system", "content": self._system_prompt}]

    def add_user_message(self, text: str):
        """Add user spoken input message."""
        if text.strip():
            self.messages.append({"role": "user", "content": text.strip()})
            logger.debug(f"Added User Message: '{text}'")

    def add_assistant_message(self, text: str):
        """Add assistant spoken output response message."""
        if text.strip():
            self.messages.append({"role": "assistant", "content": text.strip()})
            logger.debug(f"Added Assistant Message: '{text}'")

    def get_messages(self) -> List[Dict[str, str]]:
        """Return raw list of message dictionaries."""
        return self.messages

    def clear(self):
        """Clear history and restore system prompt."""
        self._reset()
        logger.info("Conversation history cleared.")
