import tempfile

import azure.cognitiveservices.speech as speechsdk

from .config import get_speech_config


def _check_result(result: speechsdk.SpeechRecognitionResult) -> str:
    """Check recognition result and return text or raise an error."""
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError(
            f"No speech recognized: {result.no_match_details}"
        )
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"Recognition canceled: {details.reason}"
        if details.error_details:
            msg += f" -- {details.error_details}"
        raise RuntimeError(msg)
    raise RuntimeError(f"Unexpected result reason: {result.reason}")


def transcribe_from_microphone() -> str:
    """Recognize speech from the default microphone (single utterance)."""
    config = get_speech_config()
    audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config, audio_config=audio
    )
    result = recognizer.recognize_once_async().get()
    return _check_result(result)


def transcribe_from_wav(file_path: str) -> str:
    """Recognize speech from a WAV file."""
    config = get_speech_config()
    audio = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config, audio_config=audio
    )
    result = recognizer.recognize_once_async().get()
    return _check_result(result)


def transcribe_from_wav_bytes(wav_bytes: bytes) -> str:
    """Recognize speech from in-memory WAV bytes."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        tmp_path = f.name
    try:
        return transcribe_from_wav(tmp_path)
    finally:
        import os
        os.unlink(tmp_path)
