import hashlib

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()

st.header("Chat with AI")
st.write(
    "Speak into your microphone, send your words to a language model, "
    "and hear the response spoken back."
)

# ── Voice selection ────────────────────────────────────────────────────────
DEFAULT_VOICES = [
    {"name": "en-US-JennyNeural", "local_name": "Jenny", "gender": "Female"},
    {"name": "en-US-GuyNeural", "local_name": "Guy", "gender": "Male"},
    {"name": "en-US-AriaNeural", "local_name": "Aria", "gender": "Female"},
    {"name": "en-US-DavisNeural", "local_name": "Davis", "gender": "Male"},
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

selected_label = st.selectbox("Response voice", options=list(voice_options.keys()))
voice_name = voice_options[selected_label]

# ── System prompt ──────────────────────────────────────────────────────────
system_prompt = st.text_area(
    "System prompt (optional)",
    value="You are a helpful assistant. Keep your responses concise -- no more than two or three sentences.",
    height=80,
)

# ── Step 1: Record audio ──────────────────────────────────────────────────
st.subheader("1. Speak")
st.write("Click the microphone icon, speak, then click again to stop.")
audio_bytes = audio_recorder(
    text="",
    recording_color="#e74c3c",
    neutral_color="#6c757d",
    pause_threshold=3.0,
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    # ── Step 2: Transcribe ─────────────────────────────────────────────────
    audio_hash = hashlib.md5(audio_bytes).hexdigest()
    if st.session_state.get("chat_audio_hash") != audio_hash:
        with st.spinner("Transcribing your speech..."):
            try:
                from speech_lib import transcribe_from_wav_bytes
                text = transcribe_from_wav_bytes(audio_bytes)
                st.session_state["chat_audio_hash"] = audio_hash
                st.session_state["chat_transcription"] = text
                # Clear prior LLM response when new audio arrives
                st.session_state.pop("chat_llm_response", None)
            except RuntimeError as e:
                st.error(f"Transcription failed: {e}")
                st.session_state["chat_transcription"] = None

    transcription = st.session_state.get("chat_transcription")
    if transcription:
        st.subheader("2. You said")
        st.info(transcription)

        # ── Step 3: Send to language model ─────────────────────────────────
        if st.button("Send to AI"):
            with st.spinner("Thinking..."):
                try:
                    from speech_lib.llm import chat
                    response = chat(transcription, system_message=system_prompt)
                    st.session_state["chat_llm_response"] = response
                except RuntimeError as e:
                    st.error(f"Language model call failed: {e}")

        llm_response = st.session_state.get("chat_llm_response")
        if llm_response:
            st.subheader("3. AI responded")
            st.success(llm_response)

            # ── Step 4: Speak the response ─────────────────────────────────
            with st.spinner("Synthesizing speech..."):
                try:
                    from speech_lib import synthesize_to_bytes
                    response_audio = synthesize_to_bytes(
                        llm_response, voice_name=voice_name,
                    )
                    st.audio(response_audio, format="audio/wav", autoplay=True)
                except RuntimeError as e:
                    st.error(f"Speech synthesis failed: {e}")
