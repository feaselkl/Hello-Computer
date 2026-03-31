import hashlib

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()

st.header("Speech to Text")
st.write("Transcribe speech from your microphone or an uploaded WAV file.")

tab_mic, tab_upload = st.tabs(["Record from Microphone", "Upload WAV File"])

# ── Microphone tab ──────────────────────────────────────────────────────────
with tab_mic:
    st.write("Click the microphone icon, speak, then click again to stop.")
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#6c757d",
        pause_threshold=3.0,
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.get("last_mic_hash") != audio_hash:
            with st.spinner("Transcribing..."):
                try:
                    from speech_lib import transcribe_from_wav_bytes
                    text = transcribe_from_wav_bytes(audio_bytes)
                    st.session_state["last_mic_hash"] = audio_hash
                    st.session_state["last_mic_text"] = text
                except RuntimeError as e:
                    st.error(f"Transcription failed: {e}")
                    st.session_state["last_mic_text"] = None

        if st.session_state.get("last_mic_text"):
            st.success(st.session_state["last_mic_text"])

# ── Upload tab ──────────────────────────────────────────────────────────────
with tab_upload:
    uploaded = st.file_uploader(
        "Choose a WAV file", type=["wav"], key="stt_upload"
    )

    if uploaded is not None:
        wav_bytes = uploaded.getvalue()
        st.audio(wav_bytes, format="audio/wav")

        if st.button("Transcribe", key="btn_transcribe_upload"):
            with st.spinner("Transcribing..."):
                try:
                    from speech_lib import transcribe_from_wav_bytes
                    text = transcribe_from_wav_bytes(wav_bytes)
                    st.success(text)
                except RuntimeError as e:
                    st.error(f"Transcription failed: {e}")
