import os
import tempfile

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.translation import (
    SpeechTranslationConfig,
    TranslationRecognizer,
)

from .config import get_speech_config


def _get_translation_config(
    source_language: str,
    target_languages: list[str],
) -> SpeechTranslationConfig:
    """Create a SpeechTranslationConfig from environment variables."""
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError(
            "Missing environment variables. "
            "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION "
            "(or create a .env file from .env.example)."
        )

    config = SpeechTranslationConfig(subscription=key, region=region)
    config.speech_recognition_language = source_language
    for lang in target_languages:
        config.add_target_language(lang)
    return config


def _check_result(
    result: speechsdk.translation.TranslationRecognitionResult,
) -> dict[str, str]:
    """Return translations dict or raise an error."""
    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        return dict(result.translations)
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        # Source recognized but no translation produced
        return {}
    if result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError(
            f"No speech recognized: {result.no_match_details}"
        )
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"Translation canceled: {details.reason}"
        if details.error_details:
            msg += f" -- {details.error_details}"
        raise RuntimeError(msg)
    raise RuntimeError(f"Unexpected result reason: {result.reason}")


def translate_from_microphone(
    source_language: str,
    target_languages: list[str],
) -> tuple[str, dict[str, str]]:
    """Translate speech from the default microphone (single utterance).

    Returns (recognized_source_text, {target_lang: translation, ...}).
    """
    config = _get_translation_config(source_language, target_languages)
    audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = TranslationRecognizer(
        translation_config=config, audio_config=audio
    )
    result = recognizer.recognize_once_async().get()
    return result.text, _check_result(result)


def translate_from_wav(
    file_path: str,
    source_language: str,
    target_languages: list[str],
) -> tuple[str, dict[str, str]]:
    """Translate speech from a WAV file (single utterance).

    Returns (recognized_source_text, {target_lang: translation, ...}).
    """
    config = _get_translation_config(source_language, target_languages)
    audio = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = TranslationRecognizer(
        translation_config=config, audio_config=audio
    )
    result = recognizer.recognize_once_async().get()
    return result.text, _check_result(result)


def translate_from_wav_bytes(
    wav_bytes: bytes,
    source_language: str,
    target_languages: list[str],
) -> tuple[str, dict[str, str]]:
    """Translate speech from in-memory WAV bytes (single utterance)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        tmp_path = f.name
    try:
        return translate_from_wav(tmp_path, source_language, target_languages)
    finally:
        os.unlink(tmp_path)


# Suggested default voices for synthesizing translated output.
# Keys are the target language codes used with add_target_language.
DEFAULT_TARGET_VOICES: dict[str, str] = {
    "en": "en-US-JennyNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "zh-Hans": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ar": "ar-SA-ZariyahNeural",
    "hi": "hi-IN-SwaraNeural",
}
