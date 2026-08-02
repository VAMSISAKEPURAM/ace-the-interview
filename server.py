"""
FastAPI Server for Voice Chatbot Backend.
Designed for local development and deployment on Hugging Face Spaces / Render.
"""

import os
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import BASE_DIR, DATA_DIR, AUDIO_DIR, GROQ_MODEL_NAME
from utils.logger import logger
from utils.timer import Timer
from utils.helpers import get_timestamped_filename, validate_environment, safe_delete_file
from services.speech_to_text import SpeechToTextService
from services.llm_service import LLMService
from services.text_to_speech import TextToSpeechService
from conversation.history import ConversationHistory
from conversation.memory import ConversationMemory
from conversation.prompt import DEFAULT_SYSTEM_PROMPT

# Validate environment settings on startup
validate_environment()

# Initialize FastAPI App
app = FastAPI(
    title="Ace The Interview - Voice AI Backend API",
    description="FastAPI Backend for Voice Chatbot powered by Hugging Face (STT/TTS) & Groq LLM",
    version="1.0.0"
)

# Enable CORS for React Frontend (Localhost & Production Vercel / HF Spaces)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
stt_service = SpeechToTextService()
llm_service = LLMService()
tts_service = TextToSpeechService()
history = ConversationHistory(system_prompt=DEFAULT_SYSTEM_PROMPT)
memory = ConversationMemory(history=history)

# Ensure runtime directories exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)



# Mount Static Files for Web UI
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_web_ui():
    """Serves the main web application UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "status": "online",
        "service": "Voice Chatbot Assistant API",
        "llm": f"Groq ({GROQ_MODEL_NAME})"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/chat/voice")
async def handle_voice_chat(file: UploadFile = File(...)):
    """
    Handles user recorded voice audio upload:
    1. Saves uploaded audio file
    2. Runs Hugging Face Speech-to-Text (STT)
    3. Queries Groq LLM
    4. Runs Hugging Face Text-to-Speech (TTS)
    5. Returns transcribed text, assistant text, and audio base64 payload.
    """
    logger.info(f"Received audio file upload: {file.filename} ({file.content_type})")
    
    # Save uploaded file
    input_path = get_timestamped_filename(prefix="user_upload", extension="wav")
    try:
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save uploaded audio file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded audio file.")

    with Timer("Voice API Pipeline"):
        # Stage 1: Speech-to-Text
        user_text = stt_service.process_audio(input_path)
        safe_delete_file(input_path)  # Cleanup uploaded temp file

        if not user_text.strip():
            return JSONResponse(content={
                "user_text": "",
                "assistant_text": "I couldn't hear any speech clearly. Could you please speak again?",
                "audio_base64": "",
                "audio_url": ""
            })

        # Stage 2: Conversation & LLM Interaction (Groq)
        history.add_user_message(user_text)
        assistant_text = llm_service.get_response(memory)
        history.add_assistant_message(assistant_text)

        # Stage 3: Text-to-Speech
        output_audio_path = tts_service.generate_speech(assistant_text)

        # Encode audio response as Base64 for instant frontend playback
        audio_base64 = ""
        if output_audio_path and output_audio_path.exists():
            try:
                with open(output_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            except Exception as read_err:
                logger.error(f"Failed to read output audio file for base64 encoding: {read_err}")

        filename = output_audio_path.name if output_audio_path else ""

        return JSONResponse(content={
            "user_text": user_text,
            "assistant_text": assistant_text,
            "audio_url": f"/api/audio/{filename}",
            "audio_base64": audio_base64
        })

@app.post("/api/chat/text")
async def handle_text_chat(text: str = Form(...)):
    """
    Handles text input fallback.
    """
    user_text = text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Text message cannot be empty.")

    with Timer("Text API Pipeline"):
        history.add_user_message(user_text)
        assistant_text = llm_service.get_response(memory)
        history.add_assistant_message(assistant_text)

        output_audio_path = tts_service.generate_speech(assistant_text)

        audio_base64 = ""
        if output_audio_path and output_audio_path.exists():
            try:
                with open(output_audio_path, "rb") as audio_file:
                    audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Error encoding audio: {e}")

        filename = output_audio_path.name if output_audio_path else ""

        return JSONResponse(content={
            "user_text": user_text,
            "assistant_text": assistant_text,
            "audio_url": f"/api/audio/{filename}",
            "audio_base64": audio_base64
        })

@app.get("/api/audio/{filename}")
def get_audio_file(filename: str):
    """
    Serves generated audio files to the frontend player.
    """
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(path=file_path, media_type="audio/wav", filename=filename)

@app.post("/api/reset")
def reset_conversation():
    """
    Resets the conversation state.
    """
    history.clear()
    return {"status": "success", "message": "Conversation history cleared."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
