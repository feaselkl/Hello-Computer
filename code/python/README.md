# Hello, Computer -- Python Demos

Azure AI Speech demos for the "Hello, Computer: An Introduction to Azure Speech" presentation.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- An Azure AI Speech resource ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices))
- For the Chat with AI demo: an Azure OpenAI deployment ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI))
- For microphone demos: a working system microphone
- On Linux: `sudo apt-get install libssl-dev libasound2-dev` (required by the Azure Speech SDK)

## Setup

```bash
cd code/python

# Create your .env file with your Azure credentials
cp .env.example .env
# Edit .env -- set AZURE_SPEECH_KEY, AZURE_SPEECH_REGION,
# and optionally AZURE_OPENAI_* variables for the Chat with AI demo

# Install dependencies
uv sync
```

## CLI Usage

Speech-to-text from your microphone:

```bash
uv run python cli.py stt
```

Speech-to-text from a WAV file:

```bash
uv run python cli.py stt --file path/to/audio.wav
```

Text-to-speech (plays through your speaker):

```bash
uv run python cli.py tts --text "Hello, Computer!"
```

Text-to-speech saved to a WAV file:

```bash
uv run python cli.py tts --text "Hello, Computer!" --output hello.wav
```

Text-to-speech with a specific voice:

```bash
uv run python cli.py tts --text "Hello, Computer!" --voice en-US-GuyNeural
```

## Streamlit Dashboard

```bash
uv run streamlit run app.py
```

This opens a browser with three pages:

- **Speech to Text** -- record from your microphone or upload a WAV file to transcribe
- **Text to Speech** -- type text, choose a voice, and play the synthesized audio
- **Chat with AI** -- speak into your microphone, send the transcription to an Azure AI Foundry language model, and hear the response spoken back

## Project Structure

```
code/python/
  pyproject.toml          Project config and dependencies
  .env.example            Template for Azure credentials
  cli.py                  Command-line interface
  app.py                  Streamlit entry point
  pages/
    1_Speech_to_Text.py   STT demo page
    2_Text_to_Speech.py   TTS demo page
    3_Chat_with_AI.py     STT -> LLM -> TTS demo page
  speech_lib/
    __init__.py            Public API
    config.py              Azure SDK configuration
    stt.py                 Speech-to-text functions
    tts.py                 Text-to-speech functions
    llm.py                 Azure AI Foundry chat completions
```
