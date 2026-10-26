
"""Speech-to-text, Gemini response generation, and text-to-speech services."""

import os
import wave
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def _get_api_key() -> str:
    """Read the key from Streamlit Cloud secrets or a local .env file."""
    try:
        key = st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        key = ""

    return key or os.getenv("GOOGLE_API_KEY", "")


_api_key = _get_api_key()

if not _api_key:
    raise RuntimeError(
        "GOOGLE_API_KEY is missing. Add it to your local .env "
        "file or Streamlit Community Cloud app secrets."
    )

client = genai.Client(api_key=_api_key)


def transcribe_audio(audio_bytes: bytes) -> str:
    """Convert recorded WAV audio to text using Gemini."""
    if not audio_bytes:
        raise ValueError("No audio was provided.")

    result = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav",
            ),
            (
                "Transcribe the spoken audio accurately. "
                "Return only the spoken words, without explanations."
            ),
        ],
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )

    transcript = (result.text or "").strip()

    if not transcript:
        raise RuntimeError("Gemini returned an empty transcription.")

    return transcript


def generate_response(
    user_text: str,
    conversation_history: list[dict],
) -> str:
    """Generate a conversational response using Gemini."""
    if not user_text.strip():
        raise ValueError("User text cannot be empty.")

    history = []

    # Keep only valid user/assistant messages.
    for item in conversation_history[-20:]:
        role = item.get("role")
        content = item.get("content")

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        # Gemini uses "model" instead of "assistant".
        gemini_role = "model" if role == "assistant" else "user"

        history.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content)],
            )
        )

    # Add the latest user message.
    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_text)],
        )
    )

    result = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a friendly voice-based AI assistant. "
                "Respond naturally and clearly. Keep answers concise "
                "for speech unless the user asks for detail. "
                "If you are uncertain, say so."
            ),
            temperature=0.7,
        ),
    )

    answer = (result.text or "").strip()

    if not answer:
        raise RuntimeError("Gemini returned an empty response.")

    return answer


def text_to_speech(text: str) -> bytes:
    """Convert text to speech using Gemini's native audio generation."""
    if not text.strip():
        raise ValueError("Text cannot be empty.")

    result = client.models.generate_content(
        model="gemini-3.8-flash-lite-tts",
        contents=text[:4000],
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore",
                    )
                )
            ),
        ),
    )

    # Gemini TTS returns audio data inside an inline audio part.
    for candidate in result.candidates or []:
        content = candidate.content

        if not content or not content.parts:
            continue

        for part in content.parts:
            if part.inline_data and part.inline_data.data:
                audio_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or ""

                # Gemini commonly returns raw 24 kHz, 16-bit PCM.
                # Wrap PCM in a WAV container for st.audio().
                if "pcm" in mime_type.lower():
                    wav_buffer = BytesIO()

                    with wave.open(wav_buffer, "wb") as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(24000)
                        wav_file.writeframes(audio_bytes)

                    return wav_buffer.getvalue()

                # Already encoded audio can be returned as-is.
                return audio_bytes

    raise RuntimeError("Gemini did not return audio data.")
