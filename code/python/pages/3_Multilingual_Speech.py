import hashlib

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()

st.header("Multi-Lingual Speech Translation")
st.write(
    "Translate spoken audio from one language to another in real time. "
    "Record from your microphone or upload a WAV file."
)

# ── Language selection ──────────────────────────────────────────────────────
SOURCE_LANGUAGES = {
    "English (US)": "en-US",
    "Mandarin Chinese": "zh-CN",
    "Spanish (Spain)": "es-ES",
    "French (France)": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Portuguese (Brazil)": "pt-BR",
    "Russian": "ru-RU",
    "Arabic (Saudi Arabia)": "ar-SA",
    "Hindi": "hi-IN",
}

TARGET_LANGUAGES = {
    "English": "en",
    "Chinese (Simplified)": "zh-Hans",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
    "Hindi": "hi",
}

col_src, col_tgt = st.columns(2)
with col_src:
    source_label = st.selectbox(
        "Source language (spoken)",
        options=list(SOURCE_LANGUAGES.keys()),
        index=1,  # Mandarin by default -- matches the slides
    )
    source_language = SOURCE_LANGUAGES[source_label]
with col_tgt:
    target_labels = st.multiselect(
        "Target language(s)",
        options=list(TARGET_LANGUAGES.keys()),
        default=["English"],
    )
    target_languages = [TARGET_LANGUAGES[label] for label in target_labels]

speak_translation = st.checkbox(
    "Also speak the translation (speech-to-speech)", value=False
)

tab_mic, tab_upload = st.tabs(["Record from Microphone", "Upload WAV File"])


def _run_translation(wav_bytes: bytes, cache_key: str) -> None:
    """Translate WAV bytes and stash results in session_state under cache_key."""
    from speech_lib import translate_from_wav_bytes

    with st.spinner("Translating..."):
        try:
            recognized, translations = translate_from_wav_bytes(
                wav_bytes, source_language, target_languages
            )
            st.session_state[f"{cache_key}_recognized"] = recognized
            st.session_state[f"{cache_key}_translations"] = translations
            st.session_state[f"{cache_key}_error"] = None
        except RuntimeError as e:
            st.session_state[f"{cache_key}_error"] = str(e)
            st.session_state[f"{cache_key}_recognized"] = None
            st.session_state[f"{cache_key}_translations"] = None


def _render_results(cache_key: str) -> None:
    error = st.session_state.get(f"{cache_key}_error")
    if error:
        st.error(f"Translation failed: {error}")
        return

    recognized = st.session_state.get(f"{cache_key}_recognized")
    translations = st.session_state.get(f"{cache_key}_translations")
    if not recognized and not translations:
        return

    if recognized:
        st.subheader("Recognized source")
        st.info(recognized)

    if translations:
        st.subheader("Translations")
        for lang, text in translations.items():
            st.markdown(f"**{lang}:** {text}")

        if speak_translation:
            _speak_translations(translations, cache_key)


def _speak_translations(translations: dict[str, str], cache_key: str) -> None:
    from speech_lib import DEFAULT_TARGET_VOICES, synthesize_to_bytes

    for lang, text in translations.items():
        voice = DEFAULT_TARGET_VOICES.get(lang)
        if not voice:
            st.caption(f"(No default voice configured for {lang})")
            continue
        audio_key = f"{cache_key}_audio_{lang}"
        if audio_key not in st.session_state:
            try:
                st.session_state[audio_key] = synthesize_to_bytes(
                    text, voice_name=voice
                )
            except RuntimeError as e:
                st.warning(f"Could not synthesize {lang}: {e}")
                continue
        st.audio(st.session_state[audio_key], format="audio/wav")


# ── Microphone tab ──────────────────────────────────────────────────────────
with tab_mic:
    if not target_languages:
        st.warning("Select at least one target language.")
    else:
        st.write("Click the microphone icon, speak, then click again to stop.")
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#6c757d",
            pause_threshold=3.0,
            key="translate_recorder",
        )

        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            audio_hash = hashlib.md5(
                audio_bytes
                + source_language.encode()
                + ",".join(target_languages).encode()
            ).hexdigest()
            if st.session_state.get("translate_mic_hash") != audio_hash:
                # Clear any cached synthesized audio from a previous run
                for k in list(st.session_state.keys()):
                    if k.startswith("translate_mic_audio_"):
                        del st.session_state[k]
                _run_translation(audio_bytes, "translate_mic")
                st.session_state["translate_mic_hash"] = audio_hash
            _render_results("translate_mic")

# ── Upload tab ──────────────────────────────────────────────────────────────
with tab_upload:
    if not target_languages:
        st.warning("Select at least one target language.")
    else:
        uploaded = st.file_uploader(
            "Choose a WAV file", type=["wav"], key="translate_upload"
        )
        if uploaded is not None:
            wav_bytes = uploaded.getvalue()
            st.audio(wav_bytes, format="audio/wav")
            if st.button("Translate", key="btn_translate_upload"):
                # Fresh run: clear prior synthesized audio
                for k in list(st.session_state.keys()):
                    if k.startswith("translate_upload_audio_"):
                        del st.session_state[k]
                _run_translation(wav_bytes, "translate_upload")
            _render_results("translate_upload")
