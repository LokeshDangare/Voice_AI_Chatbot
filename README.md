# Voice_AI_Chatbot


A turn-based voice chatbot:
1. Record a message in your browser.
2. Convert speech to text.
3. Send the text and recent conversation context to an LLM.
4. Convert the answer to MP3 speech and play it.

## Requirements

- Python 3.11 or 3.12 recommended
- Google Gemini API key
- Internet connection
- Microphone and a modern browser


## Run locally (Windows / VS Code)

Open a terminal in this project folder.

```powershell
py -3.12 -m venv voice
voice\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example to .env
```

Edit `.env` and replace the placeholder with your own API key:

```dotenv
GOOGLE_API_KEY=your_actual_key
```

Start the app:

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal (usually http://localhost:8501). Allow microphone access, record a message, then click **Process voice message**.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `voice_service.py`, `requirements.txt`, `.gitignore`, `README.md`, and `.streamlit/config.toml`.
3. Do **not** upload `.env` or `.streamlit/secrets.toml`.
4. On https://share.streamlit.io, create an app from the repository and select `app.py`.
5. In the app's settings, open **Secrets** and add:

```toml
GOOGLE_API_KEY = "your_actual_key"
```

6. Deploy or reboot the app.

## Files

- `app.py`: Streamlit UI, microphone capture, conversation display and audio playback.
- `voice_service.py`: OpenAI speech transcription, chat completion and speech generation.
- `requirements.txt`: Python packages.
- `.env.example`: Example local environment configuration.
- `.streamlit/config.toml`: Streamlit theme settings.
- `.streamlit/secrets.toml.example`: Example secrets format. Do not deploy this example file as real secrets.

## Troubleshooting

- **Missing API key:** Check `.env` locally or Streamlit Cloud app Secrets. Restart the app after changing secrets.
- **401 / authentication error:** Verify the key and that it has not been revoked.
- **429 / quota error:** Check API billing, project limits and usage.
- **Microphone does not work:** Allow microphone permission in the browser. Use HTTPS for deployed apps.
- **Model unavailable:** Confirm that your API project has access to the configured transcription, chat, and TTS models. If not, change the model names in `voice_service.py` to models available to your account.
- **Slow responses:** This prototype calls transcription, chat, and TTS sequentially; it is not a real-time streaming voice agent.

## Security and privacy

Audio is sent to the configured AI provider for transcription. The text is sent to the LLM and the response text is sent to text-to-speech. Do not use confidential or sensitive audio unless you have assessed the provider's data handling and obtained appropriate consent.
