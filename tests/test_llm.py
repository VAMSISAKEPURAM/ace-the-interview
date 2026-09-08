"""
Unit tests for Groq LLM model configuration and response sanitization.
"""

import unittest
from unittest.mock import MagicMock
from models.groq_model import FALLBACK_MODELS, GroqModel
from services.llm_service import LLMService
from conversation.memory import ConversationMemory
from conversation.history import ConversationHistory
from config import GROQ_MODEL_NAME

class TestLLMServiceAndModels(unittest.TestCase):
    def test_default_model_configured(self):
        self.assertEqual(GROQ_MODEL_NAME, "openai/gpt-oss-120b")
        self.assertIn("openai/gpt-oss-120b", FALLBACK_MODELS)
        self.assertIn("openai/gpt-oss-20b", FALLBACK_MODELS)
        self.assertIn("groq/compound-mini", FALLBACK_MODELS)

    def test_llm_service_strips_think_tags(self):
        mock_model = MagicMock()
        mock_model.generate_response.return_value = (
            "<think>Thinking about candidate experience and STAR framework...</think>"
            "I have extensive experience working with PyTorch and distributed training."
        )

        history = ConversationHistory(system_prompt="System Prompt")
        history.add_user_message("Tell me about yourself")
        memory = ConversationMemory(history=history)

        service = LLMService(llm_model=mock_model)
        result = service.get_response(memory)

        self.assertNotIn("<think>", result)
        self.assertNotIn("</think>", result)
        self.assertNotIn("Thinking about candidate", result)
        self.assertEqual(result, "I have extensive experience working with PyTorch and distributed training.")

    def test_llm_service_strips_markdown_formatting(self):
        mock_model = MagicMock()
        mock_model.generate_response.return_value = "### Technical Answer: **Strong** candidate response."

        history = ConversationHistory(system_prompt="System Prompt")
        history.add_user_message("What are your strengths?")
        memory = ConversationMemory(history=history)

        service = LLMService(llm_model=mock_model)
        result = service.get_response(memory)

        self.assertNotIn("*", result)
        self.assertNotIn("#", result)
        self.assertIn("Technical Answer: Strong candidate response.", result)

if __name__ == "__main__":
    unittest.main()
