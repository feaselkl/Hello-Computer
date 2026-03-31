import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


def get_speech_config() -> speechsdk.SpeechConfig:
    """Create a SpeechConfig from environment variables.

    Requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.
    """
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")

    if not key or not region:
        raise RuntimeError(
            "Missing environment variables. "
            "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION "
            "(or create a .env file from .env.example)."
        )

    return speechsdk.SpeechConfig(subscription=key, region=region)
