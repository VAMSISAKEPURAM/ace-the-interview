"""
Ace The Interview - Main Entry Point & Hugging Face Spaces Deployment.
Provides Web Voice Chatbot Interface powered by Gradio (100% FREE on HF Spaces).
"""

import os
from pathlib import Path
import gradio as gr
from config import DEFAULT_RECORD_DURATION, GROQ_MODEL_NAME
from utils.logger import logger
from utils.timer import Timer
from utils.helpers import validate_environment, safe_delete_file
from services.speech_to_text import SpeechToTextService
from services.llm_service import LLMService
from services.text_to_speech import TextToSpeechService
from conversation.history import ConversationHistory
from conversation.memory import ConversationMemory
from conversation.prompt import DEFAULT_SYSTEM_PROMPT

# Validate environment settings on startup
validate_environment()

# Initialize Core Services
stt_service = SpeechToTextService()
llm_service = LLMService()
tts_service = TextToSpeechService()
history = ConversationHistory(system_prompt=DEFAULT_SYSTEM_PROMPT)
# Hugging Face ZeroGPU Integration
try:
    import spaces
    has_zero_gpu = True
except ImportError:
    has_zero_gpu = False

if has_zero_gpu:
    @spaces.GPU
    def process_voice_turn(audio_path, chat_transcript):
        return _process_voice_turn_impl(audio_path, chat_transcript)
else:
    def process_voice_turn(audio_path, chat_transcript):
        return _process_voice_turn_impl(audio_path, chat_transcript)

def _process_voice_turn_impl(audio_path, chat_transcript):
    """
    Processes one voice turn:
    User Audio -> HF STT -> Groq LLM -> HF TTS -> Voice Response
    """


    if audio_path is None:
        return None, chat_transcript, "Please record or upload your voice audio."

    if chat_transcript is None:
        chat_transcript = []

    with Timer("Voice Turn Pipeline"):
        # Step 1: Speech-to-Text
        user_text = stt_service.process_audio(Path(audio_path))
        if not user_text.strip():
            return None, chat_transcript, "Could not recognize speech. Please speak again."

        # Step 2: LLM Response (Groq LLaMA 3.3)
        history.add_user_message(user_text)
        assistant_text = llm_service.get_response(memory)
        history.add_assistant_message(assistant_text)

        # Step 3: Text-to-Speech
        output_audio_path = tts_service.generate_speech(assistant_text)

        # Update Chat Transcript for Gradio UI
        chat_transcript.append((user_text, assistant_text))

        return str(output_audio_path), chat_transcript, f"Speech processed! Model: Groq ({GROQ_MODEL_NAME})"

def reset_chat():
    """Reset history and memory."""
    history.clear()
    return None, [], "Conversation reset."

# Build Gradio Web Interface
with gr.Blocks(theme=gr.themes.Soft(), title="Ace The Interview - Voice AI") as demo:
    gr.Markdown(
        """
        # 🎙️ Ace The Interview - Voice AI Assistant
        **Powered by Groq Cloud API (LLaMA 3.3)** &amp; **Hugging Face STT/TTS (Whisper & MMS)**
        
        Click the **Microphone** button below, speak your answer or question, and click **Submit Voice**!
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="🎤 Record Your Voice",
                interactive=True
            )
            submit_btn = gr.Button("🚀 Submit Voice Response", variant="primary")
            reset_btn = gr.Button("🧹 Reset Conversation", variant="secondary")
            status_output = gr.Textbox(label="Status / Diagnostics", value="Ready", interactive=False)

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="💬 Interview Transcript", height=400)
            audio_output = gr.Audio(label="🔊 Assistant Spoken Response", autoplay=True)

    # Event Bindings
    submit_btn.click(
        fn=process_voice_turn,
        inputs=[audio_input, chatbot],
        outputs=[audio_output, chatbot, status_output]
    )

    reset_btn.click(
        fn=reset_chat,
        inputs=[],
        outputs=[audio_input, chatbot, status_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
