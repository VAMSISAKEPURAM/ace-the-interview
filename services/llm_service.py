"""
Language Model (LLM) Service Layer.
Manages LLM provider interactions and response sanitization.
"""

import re
from typing import List, Dict
from models.groq_model import GroqModel
from conversation.memory import ConversationMemory
from utils.logger import logger

class LLMService:
    """
    Service layer orchestrating LLM queries via Groq Cloud.
    """
    def __init__(self, llm_model: GroqModel = None):
        self.llm_model = llm_model or GroqModel()


    def get_response(self, conversation_memory: ConversationMemory) -> str:
        """
        Retrieves pruned message history from memory and queries LLM model.
        """
        messages = conversation_memory.get_pruned_messages()
        if not messages:
            logger.warning("Empty conversation messages provided to LLM Service.")
            return "How can I assist you today?"

        response_text = self.llm_model.generate_response(messages)
        
        # Clean response text: strip reasoning thoughts and audio synthesis artifacts (e.g. markdown asterisks)
        cleaned_text = re.sub(r"<think>[\s\S]*?</think>", "", response_text, flags=re.IGNORECASE).strip()
        cleaned_text = cleaned_text.replace("*", "").replace("#", "").strip()
        return cleaned_text
