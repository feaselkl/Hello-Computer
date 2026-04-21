import hashlib
import json

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()

st.header("Pronunciation Assessment")
st.write(
    "Read a reference sentence out loud and Azure AI Speech will score your "
    "pronunciation, fluency, completeness, and prosody -- with a word-by-word breakdown."
)

# ── Reference text ──────────────────────────────────────────────────────────
from speech_lib import AssessmentResult, load_samples

try:
    SAMPLES = load_samples()
except Exception as e:
    st.error(f"Could not load samples: {e}")
    SAMPLES = []

CUSTOM_OPTION = "-- Custom text --"
sample_titles = [s.get("title", "(untitled)") for s in SAMPLES] + [CUSTOM_OPTION]
selected_title = st.selectbox("Reference sample", options=sample_titles)

if selected_title == CUSTOM_OPTION:
    reference_text = st.text_area(
        "Reference text (what you intend to read aloud)",
        value="Hello, computer.",
        height=100,
    )
    language = st.selectbox(
        "Language",
        options=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "ja-JP", "zh-CN"],
        index=0,
    )
else:
    sample = next(s for s in SAMPLES if s.get("title") == selected_title)
    reference_text = sample.get("text", "")
    language = sample.get("language", "en-US")
    st.text_area(
        "Reference text (read this aloud)",
        value=reference_text,
        height=100,
        disabled=True,
    )
    st.caption(f"Language: `{language}`")

# ── Reset state when the reference sample, language, or text changes ───────
# Otherwise an old recording gets reprocessed against the new reference text,
# and stale assessments linger against the wrong sample.
_pron_ctx = f"{selected_title}|{language}|{reference_text}"
if st.session_state.get("_pron_ctx") != _pron_ctx:
    for _k in (
        "pron_recorder",
        "pron_upload",
        "pron_mic_hash",
        "pron_mic_result",
        "pron_mic_result_error",
        "pron_upload_result",
        "pron_upload_result_error",
    ):
        st.session_state.pop(_k, None)
    st.session_state["_pron_ctx"] = _pron_ctx

# ── Rendering helpers ───────────────────────────────────────────────────────
ERROR_COLORS = {
    "None": "#d4edda",            # green-ish (good)
    "Mispronunciation": "#fff3cd",  # yellow
    "Omission": "#f8d7da",         # red
    "Insertion": "#f5c2c7",        # pinkish red
    "UnexpectedBreak": "#ffe5b4",  # light orange
    "MissingBreak": "#ffe5b4",
    "Monotone": "#e2e3e5",         # grey
}


def _score_color(score: float | None) -> str:
    if score is None:
        return "#e2e3e5"
    if score >= 80:
        return "#d4edda"
    if score >= 60:
        return "#fff3cd"
    return "#f8d7da"


def _render_scores(result: AssessmentResult) -> None:
    st.subheader("Scores")
    cols = st.columns(5)
    pairs = [
        ("Pronunciation", result.pronunciation_score),
        ("Accuracy", result.accuracy_score),
        ("Fluency", result.fluency_score),
        ("Completeness", result.completeness_score),
        ("Prosody", result.prosody_score),
    ]
    for col, (label, score) in zip(cols, pairs):
        with col:
            if score is None:
                st.metric(label, "--")
            else:
                st.metric(label, f"{score:.1f}")


def _render_words(result: AssessmentResult) -> None:
    st.subheader("Word-by-word breakdown")

    parts: list[str] = []
    for w in result.words:
        bg = ERROR_COLORS.get(w.error_type, "#e2e3e5")
        if w.error_type == "None" and w.accuracy_score is not None:
            bg = _score_color(w.accuracy_score)
        score_text = (
            f"<br/><small>{w.accuracy_score:.0f}</small>"
            if w.accuracy_score is not None
            else ""
        )
        error_badge = (
            f"<br/><small><em>{w.error_type}</em></small>"
            if w.error_type and w.error_type != "None"
            else ""
        )
        parts.append(
            f"<span style='background:{bg};padding:4px 8px;margin:2px;"
            f"border-radius:4px;display:inline-block;text-align:center;"
            f"font-family:sans-serif;'>"
            f"<strong>{w.word}</strong>{score_text}{error_badge}"
            f"</span>"
        )
    st.markdown(
        "<div style='line-height:2.2;'>" + "".join(parts) + "</div>",
        unsafe_allow_html=True,
    )

    _render_legend()


def _render_legend() -> None:
    legend = [
        ("Good (≥80)", "#d4edda"),
        ("Fair (60-79)", "#fff3cd"),
        ("Poor (<60)", "#f8d7da"),
        ("Omission/Insertion", "#f5c2c7"),
        ("Break issue", "#ffe5b4"),
        ("Monotone", "#e2e3e5"),
    ]
    chips = "".join(
        f"<span style='background:{c};padding:2px 8px;margin:2px;border-radius:4px;"
        f"font-size:0.85em;'>{label}</span>"
        for label, c in legend
    )
    st.markdown(
        f"<div style='margin-top:0.5rem;'><small>Legend: {chips}</small></div>",
        unsafe_allow_html=True,
    )


def _render_error_summary(result: AssessmentResult) -> None:
    non_none = [w for w in result.words if w.error_type and w.error_type != "None"]
    if not non_none:
        st.success("No pronunciation errors detected.")
        return
    st.subheader("Errors detected")
    counts: dict[str, int] = {}
    for w in non_none:
        counts[w.error_type] = counts.get(w.error_type, 0) + 1
    summary = ", ".join(f"**{k}**: {v}" for k, v in counts.items())
    st.markdown(summary)

    with st.expander(f"All flagged words ({len(non_none)})"):
        for w in non_none:
            score = f"{w.accuracy_score:.0f}" if w.accuracy_score is not None else "--"
            st.markdown(f"- `{w.word}` -- {w.error_type} (accuracy: {score})")


def _render_phoneme_details(result: AssessmentResult) -> None:
    words_with_phonemes = [w for w in result.words if w.phonemes]
    if not words_with_phonemes:
        return
    with st.expander("Phoneme-level detail"):
        for w in words_with_phonemes:
            st.markdown(f"**{w.word}**")
            chips = []
            for p in w.phonemes:
                bg = _score_color(p.accuracy_score)
                score = f"{p.accuracy_score:.0f}" if p.accuracy_score is not None else "--"
                chips.append(
                    f"<span style='background:{bg};padding:3px 6px;margin:2px;"
                    f"border-radius:3px;font-family:monospace;'>"
                    f"{p.phoneme} <small>({score})</small></span>"
                )
            st.markdown(
                "<div style='line-height:2;'>" + "".join(chips) + "</div>",
                unsafe_allow_html=True,
            )


def _render_results(result: AssessmentResult) -> None:
    if result.recognized_text:
        st.subheader("Recognized speech")
        st.info(result.recognized_text)
    _render_scores(result)
    _render_words(result)
    _render_error_summary(result)
    _render_phoneme_details(result)
    with st.expander("Raw JSON"):
        st.code(json.dumps(result.raw_json, indent=2, ensure_ascii=False), language="json")


# ── Run assessment ──────────────────────────────────────────────────────────
def _run_assessment(wav_bytes: bytes, cache_key: str) -> None:
    from speech_lib import assess_from_wav_bytes

    with st.spinner("Assessing pronunciation..."):
        try:
            result = assess_from_wav_bytes(wav_bytes, reference_text, language)
            st.session_state[cache_key] = result
            st.session_state[f"{cache_key}_error"] = None
        except RuntimeError as e:
            st.session_state[f"{cache_key}_error"] = str(e)
            st.session_state[cache_key] = None


def _render_cached(cache_key: str) -> None:
    err = st.session_state.get(f"{cache_key}_error")
    if err:
        st.error(f"Assessment failed: {err}")
        return
    result = st.session_state.get(cache_key)
    if result:
        _render_results(result)


tab_mic, tab_upload = st.tabs(["Record from Microphone", "Upload WAV File"])

with tab_mic:
    if not reference_text.strip():
        st.warning("Enter or select reference text first.")
    else:
        st.write("Click the microphone icon, read the reference aloud, then click again to stop.")
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#6c757d",
            pause_threshold=3.0,
            key="pron_recorder",
        )
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            audio_hash = hashlib.md5(audio_bytes).hexdigest()
            if st.session_state.get("pron_mic_hash") != audio_hash:
                _run_assessment(audio_bytes, "pron_mic_result")
                st.session_state["pron_mic_hash"] = audio_hash
            _render_cached("pron_mic_result")

with tab_upload:
    if not reference_text.strip():
        st.warning("Enter or select reference text first.")
    else:
        uploaded = st.file_uploader(
            "Choose a WAV file", type=["wav"], key="pron_upload"
        )
        if uploaded is not None:
            wav_bytes = uploaded.getvalue()
            st.audio(wav_bytes, format="audio/wav")
            if st.button("Assess pronunciation", key="btn_pron_upload"):
                _run_assessment(wav_bytes, "pron_upload_result")
            _render_cached("pron_upload_result")
