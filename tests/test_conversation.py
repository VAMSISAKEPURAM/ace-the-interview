"""
Unit tests for conversation history and memory pruning.
"""

import unittest
from conversation.history import ConversationHistory
from conversation.memory import ConversationMemory

class TestConversationSystem(unittest.TestCase):
    def test_conversation_history(self):
        history = ConversationHistory(system_prompt="Test System Prompt")
        messages = history.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "Test System Prompt")

        history.add_user_message("Hello")
        history.add_assistant_message("Hi there!")

        messages = history.get_messages()
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[2]["role"], "assistant")

    def test_conversation_memory_pruning(self):
        history = ConversationHistory(system_prompt="Test System Prompt")
        memory = ConversationMemory(history=history, max_messages=2)

        # Add 4 messages (2 turns)
        history.add_user_message("Q1")
        history.add_assistant_message("A1")
        history.add_user_message("Q2")
        history.add_assistant_message("A2")

        pruned = memory.get_pruned_messages()
        # Should contain system message + last 2 messages (Q2, A2)
        self.assertEqual(len(pruned), 3)
        self.assertEqual(pruned[0]["role"], "system")
        self.assertEqual(pruned[1]["content"], "Q2")
        self.assertEqual(pruned[2]["content"], "A2")

if __name__ == "__main__":
    unittest.main()

