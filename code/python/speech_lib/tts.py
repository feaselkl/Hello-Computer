from __future__ import annotations

import os

import azure.cognitiveservices.speech as speechsdk

from .config import get_speech_config


def _configure_voice(
    config: speechsdk.SpeechConfig,
    voice_name: str,
    endpoint_id: str | None = None,
) -> None:
    """Set voice name and optional custom endpoint on a SpeechConfig."""
    if endpoint_id:
        config.endpoint_id = endpoint_id
    config.speech_synthesis_voice_name = voice_name


def _check_synthesis(result: speechsdk.SpeechSynthesisResult) -> None:
    """Check synthesis result or raise an error."""
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"Synthesis canceled: {details.reason}"
        if details.error_details:
            msg += f" -- {details.error_details}"
        raise RuntimeError(msg)
    raise RuntimeError(f"Unexpected synthesis result: {result.reason}")


def _resolve_endpoint_id(endpoint_id: str | None) -> str | None:
    """Use the provided endpoint_id or fall back to the environment variable."""
    return endpoint_id or os.environ.get("AZURE_SPEECH_ENDPOINT_ID")


def speak_text(
    text: str,
    voice_name: str = "en-US-JennyNeural",
    endpoint_id: str | None = None,
) -> None:
    """Synthesize text and play through the default speaker."""
    config = get_speech_config()
    _configure_voice(config, voice_name, _resolve_endpoint_id(endpoint_id))
    audio = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=audio
    )
    result = synthesizer.speak_text_async(text).get()
    _check_synthesis(result)


def synthesize_to_wav(
    text: str,
    output_path: str,
    voice_name: str = "en-US-JennyNeural",
    endpoint_id: str | None = None,
) -> None:
    """Synthesize text and save to a WAV file."""
    config = get_speech_config()
    _configure_voice(config, voice_name, _resolve_endpoint_id(endpoint_id))
    audio = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=audio
    )
    result = synthesizer.speak_text_async(text).get()
    _check_synthesis(result)


def synthesize_to_bytes(
    text: str,
    voice_name: str = "en-US-JennyNeural",
    endpoint_id: str | None = None,
) -> bytes:
    """Synthesize text and return WAV audio bytes."""
    config = get_speech_config()
    _configure_voice(config, voice_name, _resolve_endpoint_id(endpoint_id))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=None
    )
    result = synthesizer.speak_text_async(text).get()
    _check_synthesis(result)
    return result.audio_data


def list_voices(locale: str = "en-US") -> list[dict]:
    """Return available voices for a locale."""
    config = get_speech_config()
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=None
    )
    voices_result = synthesizer.get_voices_async(locale=locale).get()
    if voices_result.reason == speechsdk.ResultReason.VoicesListRetrieved:
        return [
            {
                "name": v.short_name,
                "local_name": v.local_name,
                "gender": str(v.gender).split(".")[-1],
            }
            for v in voices_result.voices
        ]
    raise RuntimeError(f"Failed to list voices: {voices_result.reason}")
