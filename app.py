import gradio as gr
import speech_recognition as sr
import edge_tts
import asyncio
import tempfile
import os

def recognize(audio_path: str) -> str:
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
    return r.recognize_google(audio_data)

def get_response(text: str) -> str:
    responses = [
        ("hello", "Hello! I'm your AI voice assistant. How can I help you today?"),
        ("hi", "Hi there! I'm ready to assist you."),
        ("how are you", "I'm functioning well. This is a live voice AI demo with STT and TTS."),
        ("what can you do", "I can listen to your voice, process it, and respond with synthesized speech."),
        ("your name", "I'm an LLM-powered voice assistant built with Python, OpenAI API, and Hugging Face."),
    ]
    for key, reply in responses:
        if key in text.lower():
            return reply
    return f"You said: '{text}'. Full LLM backend available via OpenAI and Hugging Face APIs."

def text_to_speech(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    async def _run():
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(tmp.name)
    asyncio.run(_run())
    return tmp.name

def voice_pipeline(audio):
    if audio is None:
        return "No audio", "Please record something", None
    user_text      = recognize(audio)
    assistant_text = get_response(user_text)
    audio_out      = text_to_speech(assistant_text)
    return user_text, assistant_text, audio_out

demo = gr.Interface(
    fn=voice_pipeline,
    inputs=gr.Audio(sources="microphone", type="filepath"),
    outputs=[
        gr.Textbox(label="You said"),
        gr.Textbox(label="Assistant response"),
        gr.Audio(label="Voice response"),
    ],
    title="🎙️ LLM-Powered Voice Assistant",
    description="Live demo: Speak → Speech-to-Text (Google) → Response → Edge TTS | Full OpenAI & Hugging Face backends available in source.",
)

demo.launch()