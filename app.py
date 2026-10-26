import hashlib
import streamlit as st

from voice_service import (
    generate_response,
    text_to_speech,
    transcribe_audio,
)

st.set_page_config(
    page_title="Voice AI Chatbot",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Voice AI Chatbot")
st.write("Speak into your microphone and your AI assistant will answer in text and voice.")
st.caption("Turn-based demo: record a message, then press Process voice message.")

# Conversation items contain role, content, and optionally audio bytes.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_audio_hashes" not in st.session_state:
    st.session_state.processed_audio_hashes = set()
if "audio_widget_version" not in st.session_state:
    st.session_state.audio_widget_version = 0

# Show previous conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("audio"):
            st.audio(message["audio"], format="audio/mp3")

st.divider()
audio = st.audio_input(
    "Record your message",
    key=f"voice_recorder_{st.session_state.audio_widget_version}",
)

if audio is not None:
    audio_bytes = audio.getvalue()
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    st.audio(audio_bytes, format="audio/wav")

    if audio_hash in st.session_state.processed_audio_hashes:
        st.info("This recording has already been processed. Record a new message to continue.")
    elif st.button("▶ Process voice message", type="primary"):
        try:
            with st.spinner("Converting speech to text..."):
                user_text = transcribe_audio(audio_bytes)

            if not user_text.strip():
                st.warning("I couldn't recognize any speech. Please try recording again.")
            else:
                st.session_state.messages.append(
                    {"role": "user", "content": user_text.strip()}
                )
                with st.spinner("Generating an answer..."):
                    # Keep the recent conversation as context; exclude audio bytes.
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[:-1]
                        if m["role"] in ("user", "assistant")
                    ][-20:]
                    answer = generate_response(user_text.strip(), history)

                with st.spinner("Creating spoken answer..."):
                    audio_answer = text_to_speech(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "audio": audio_answer,
                    }
                )
                st.session_state.processed_audio_hashes.add(audio_hash)
                st.rerun()

        except Exception as exc:
            st.error(
                "The request failed. Check your API key, internet connection, "
                "API access, and usage limits."
            )
            with st.expander("Technical details"):
                st.code(f"{type(exc).__name__}: {exc}")

col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.processed_audio_hashes = set()
        st.session_state.audio_widget_version += 1
        st.rerun()
with col2:
    if st.button("🔄 New recording", use_container_width=True):
        st.session_state.audio_widget_version += 1
        st.rerun()

st.caption("Privacy note: recorded audio is sent to the configured AI provider for processing.")
