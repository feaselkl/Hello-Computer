from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import azure.cognitiveservices.speech as speechsdk

from .config import get_speech_config


@dataclass
class PhonemeResult:
    phoneme: str
    accuracy_score: float | None


@dataclass
class SyllableResult:
    syllable: str
    accuracy_score: float | None


@dataclass
class WordResult:
    word: str
    accuracy_score: float | None
    error_type: str  # None, Mispronunciation, Omission, Insertion, UnexpectedBreak, MissingBreak, Monotone
    syllables: list[SyllableResult] = field(default_factory=list)
    phonemes: list[PhonemeResult] = field(default_factory=list)


@dataclass
class AssessmentResult:
    recognized_text: str
    pronunciation_score: float | None
    accuracy_score: float | None
    fluency_score: float | None
    completeness_score: float | None
    prosody_score: float | None
    words: list[WordResult] = field(default_factory=list)
    raw_json: dict[str, Any] = field(default_factory=dict)


def _build_config(
    reference_text: str,
    language: str,
) -> tuple[speechsdk.SpeechConfig, speechsdk.PronunciationAssessmentConfig]:
    speech_config = get_speech_config()
    speech_config.speech_recognition_language = language

    pron_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True,
    )
    # Prosody is en-US only; the SDK ignores the call on other locales.
    if language.lower().startswith("en-"):
        pron_config.enable_prosody_assessment()
    return speech_config, pron_config


def _parse_result(
    speech_result: speechsdk.SpeechRecognitionResult,
) -> AssessmentResult:
    if speech_result.reason == speechsdk.ResultReason.Canceled:
        details = speech_result.cancellation_details
        msg = f"Recognition canceled: {details.reason}"
        if details.error_details:
            msg += f" -- {details.error_details}"
        raise RuntimeError(msg)
    if speech_result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError(
            f"No speech recognized: {speech_result.no_match_details}"
        )
    if speech_result.reason != speechsdk.ResultReason.RecognizedSpeech:
        raise RuntimeError(f"Unexpected result reason: {speech_result.reason}")

    json_str = speech_result.properties.get(
        speechsdk.PropertyId.SpeechServiceResponse_JsonResult
    )
    payload = json.loads(json_str) if json_str else {}

    nbest = (payload.get("NBest") or [{}])[0]
    scores = nbest.get("PronunciationAssessment", {}) or {}
    words = [_parse_word(w) for w in nbest.get("Words", []) or []]

    return AssessmentResult(
        recognized_text=payload.get("DisplayText") or speech_result.text or "",
        pronunciation_score=scores.get("PronScore"),
        accuracy_score=scores.get("AccuracyScore"),
        fluency_score=scores.get("FluencyScore"),
        completeness_score=scores.get("CompletenessScore"),
        prosody_score=scores.get("ProsodyScore"),
        words=words,
        raw_json=payload,
    )


def _parse_word(word_json: dict[str, Any]) -> WordResult:
    scores = word_json.get("PronunciationAssessment", {}) or {}
    syllables = [
        SyllableResult(
            syllable=s.get("Syllable", ""),
            accuracy_score=(s.get("PronunciationAssessment") or {}).get("AccuracyScore"),
        )
        for s in word_json.get("Syllables", []) or []
    ]
    phonemes = [
        PhonemeResult(
            phoneme=p.get("Phoneme", ""),
            accuracy_score=(p.get("PronunciationAssessment") or {}).get("AccuracyScore"),
        )
        for p in word_json.get("Phonemes", []) or []
    ]
    return WordResult(
        word=word_json.get("Word", ""),
        accuracy_score=scores.get("AccuracyScore"),
        error_type=scores.get("ErrorType", "None"),
        syllables=syllables,
        phonemes=phonemes,
    )


def _run(
    audio_config: speechsdk.audio.AudioConfig,
    reference_text: str,
    language: str,
) -> AssessmentResult:
    speech_config, pron_config = _build_config(reference_text, language)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    pron_config.apply_to(recognizer)
    result = recognizer.recognize_once()
    return _parse_result(result)


def assess_from_microphone(
    reference_text: str, language: str = "en-US"
) -> AssessmentResult:
    """Assess pronunciation from the default microphone (single utterance)."""
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    return _run(audio_config, reference_text, language)


def assess_from_wav(
    file_path: str, reference_text: str, language: str = "en-US"
) -> AssessmentResult:
    """Assess pronunciation from a WAV file."""
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    return _run(audio_config, reference_text, language)


def assess_from_wav_bytes(
    wav_bytes: bytes, reference_text: str, language: str = "en-US"
) -> AssessmentResult:
    """Assess pronunciation from in-memory WAV bytes."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        tmp_path = f.name
    try:
        return assess_from_wav(tmp_path, reference_text, language)
    finally:
        os.unlink(tmp_path)


def load_samples(yaml_path: str | Path | None = None) -> list[dict[str, str]]:
    """Load pronunciation reference samples from a YAML file.

    Defaults to code/samples/pronunciation_inputs.yaml relative to the repo root.
    """
    import yaml

    if yaml_path is None:
        # speech_lib/pronunciation.py -> code/python/speech_lib -> up 3 to repo root
        yaml_path = Path(__file__).resolve().parents[3] / "code" / "samples" / "pronunciation_inputs.yaml"
    else:
        yaml_path = Path(yaml_path)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("samples", []) or []
