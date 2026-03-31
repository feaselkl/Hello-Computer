import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.header("Text to Speech")
st.write("Type text below and hear it spoken in a neural voice.")

# ── Voice selection ─────────────────────────────────────────────────────────
DEFAULT_VOICES = [
    {"name": "en-US-JennyNeural", "local_name": "Jenny", "gender": "Female"},
    {"name": "en-US-GuyNeural", "local_name": "Guy", "gender": "Male"},
    {"name": "en-US-AriaNeural", "local_name": "Aria", "gender": "Female"},
    {"name": "en-US-DavisNeural", "local_name": "Davis", "gender": "Male"},
    {"name": "en-GB-SoniaNeural", "local_name": "Sonia", "gender": "Female"},
    {"name": "en-AU-NatashaNeural", "local_name": "Natasha", "gender": "Female"},
]


@st.cache_data(ttl=3600, show_spinner=False)
def get_voices() -> list[dict]:
    try:
        from speech_lib import list_voices
        return list_voices(locale="en-US")
    except Exception:
        return DEFAULT_VOICES


voices = get_voices()
voice_options = {
    f"{v['local_name']} ({v['gender']}) -- {v['name']}": v["name"]
    for v in voices
}

selected_label = st.selectbox("Voice", options=list(voice_options.keys()))
voice_name = voice_options[selected_label]

# ── Personal voice (optional) ─────────────────────────────────────────────
speaker_profile_id = st.text_input(
    "Personal Voice speaker profile ID (optional)",
    value=os.environ.get("AZURE_SPEECH_SPEAKER_PROFILE_ID", ""),
    help="Set this to use a Personal Voice. Uses SSML with DragonLatestNeural. Overrides endpoint ID.",
)
speaker_profile_id = speaker_profile_id.strip() or None

# ── Text input and synthesis ────────────────────────────────────────────────
text = st.text_area(
    "Text to speak",
    value="Hello, Computer! This is Azure AI Speech.",
    height=120,
)

if st.button("Speak") and text.strip():
    with st.spinner("Synthesizing..."):
        try:
            from speech_lib import synthesize_to_bytes
            audio_bytes = synthesize_to_bytes(
                text, voice_name=voice_name,
                speaker_profile_id=speaker_profile_id,
            )
            st.audio(audio_bytes, format="audio/wav")
            st.download_button(
                "Download WAV",
                data=audio_bytes,
                file_name="speech.wav",
                mime="audio/wav",
            )
        except RuntimeError as e:
            st.error(f"Synthesis failed: {e}")
