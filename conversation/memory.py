"""
Conversation Memory Management Module.
Enforces sliding window boundaries on conversation history to prevent context overflow.
"""

from typing import List, Dict
from config import MAX_HISTORY_MESSAGES
from conversation.history import ConversationHistory
from utils.logger import logger

class ConversationMemory:
    """
    Applies memory limits and window sliding over conversation history.
    """
    def __init__(self, history: ConversationHistory, max_messages: int = MAX_HISTORY_MESSAGES):
        self.history = history
        self.max_messages = max_messages

    def get_pruned_messages(self) -> List[Dict[str, str]]:
        """
        Returns messages pruned to max_messages, preserving the initial system prompt.
        """
        all_messages = self.history.get_messages()
        if not all_messages:
            return []

        system_msg = all_messages[0] if all_messages[0]["role"] == "system" else None
        chat_messages = all_messages[1:] if system_msg else all_messages

        if len(chat_messages) > self.max_messages:
            pruned_chat = chat_messages[-self.max_messages:]
            logger.info(f"Pruned conversation history from {len(chat_messages)} to last {self.max_messages} messages.")
        else:
            pruned_chat = chat_messages

        if system_msg:
            return [system_msg] + pruned_chat
        return pruned_chat
