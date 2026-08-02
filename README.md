---
title: Ace The Interview Voice Chatbot
emoji: 🎙️
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: 4.25.0
app_file: app.py
pinned: false
short_description: Voice AI Assistant powered by Groq LLM and Hugging Face STT/TTS
---

# Ace The Interview - Voice AI Assistant

Production-ready web-based Voice Conversational AI Assistant using **Hugging Face open-source models** for Speech-to-Text (Whisper) & Text-to-Speech (MMS-TTS), and **Groq Cloud API** (`llama-3.3-70b-versatile`) for ultra-fast response generation.

---

## 🌟 Features

- 🎤 **Voice Recording & Audio Output**: Microphone input with automatic voice response playback.
- ⚡ **Groq LLaMA 3.3 LLM**: Instant responses using Groq's high-speed inference engine.
- 🧠 **Hugging Face STT & TTS**: Open-source speech transcription and audio synthesis.
- 🚀 **100% FREE Cloud Deployment**: Gradio SDK on Hugging Face Spaces (16 GB Free RAM, zero credit card required).

---

## ☁️ How to Deploy for FREE on Hugging Face Spaces (16 GB RAM)

1. Go to **[Hugging Face Spaces](https://huggingface.co/new-space)**.
2. Enter Space Name: `ace-the-interview`.
3. Under **Select the Space SDK**: Select **Gradio** (100% FREE!).
4. Under **Space Hardware**: Select **CPU Basic (Free - 16 GB RAM / 2 vCPUs)**.
5. Click **Create Space**.
6. Push all project files (`app.py`, `requirements.txt`, `config.py`, etc.) to your Space repository.
7. Go to Space **Settings** -> **Variables and Secrets**:
   - Add Secret: `GROQ_API_KEY` = your_groq_key
   - Add Secret: `HF_TOKEN` = your_hf_token
8. Your Voice AI Assistant web app will automatically build and launch for **FREE**!
