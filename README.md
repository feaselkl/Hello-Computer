# Hello, Computer: An Introduction to Azure Speech

This repository provides the supporting code for my presentation entitled [Hello, Computer: An Introduction to Azure Speech](https://www.catallaxyservices.com/presentations/hello-computer/).

## What's in the Box

Two parallel demo tracks -- Python and .NET -- covering the same scenarios so you can follow along in the language you prefer:

| Demo | What it shows | Python | .NET |
| --- | --- | --- | --- |
| **Speech to Text** | Transcribe mic input or a WAV file | CLI + Streamlit | CLI + Web |
| **Text to Speech** | Synthesize audio from text, pick voices, Personal Voice | CLI + Streamlit | CLI + Web |
| **Multi-Lingual Translation** | Translate spoken audio across languages (optional speech-to-speech) | Streamlit | Web |
| **Pronunciation Assessment** | Score pronunciation with word-by-word error tracking | Streamlit | Web |
| **Chat with AI** | Speech -> LLM -> speech (Python) / text -> LLM -> speech (.NET) | Streamlit | Web |

Both web surfaces record directly from the browser microphone in addition to accepting WAV uploads. Pronunciation reference samples are shared via [code/samples/pronunciation_inputs.yaml](code/samples/pronunciation_inputs.yaml) so both tracks read the same text prompts.

## Running the Code

### Python Demos

See [code/python/README.md](code/python/README.md) for full setup and usage. The Python track includes a CLI for speech-to-text / text-to-speech and a five-page Streamlit dashboard.

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), an Azure AI Speech resource. For the Chat with AI demo: an Azure OpenAI deployment.

```bash
cd code/python
cp .env.example .env
# Edit .env with your Azure Speech key and region
uv sync

# CLI
uv run python cli.py stt
uv run python cli.py stt --file samples/sample_english.wav
uv run python cli.py tts --text "This is a test of text to speech."
uv run python cli.py tts --text "This is a test of text to speech." --voice en-US-Phoebe:DragonHDLatestNeural

# Streamlit dashboard (Speech-to-Text, Text-to-Speech, Translation,
# Pronunciation Assessment, Chat with AI)
uv run streamlit run app.py
```

### .NET Demos

See [code/dotnet/README.md](code/dotnet/README.md) for full setup and usage. The .NET track includes a CLI for speech-to-text / text-to-speech / voice listing and a Razor Pages web app with five demos (all of which record from the browser microphone).

**Requirements:** .NET 9.0 SDK, an Azure AI Speech resource. For the Chat with AI demo: an Azure OpenAI deployment.

```bash
cd code/dotnet
cp .env.example .env
# Edit .env with your Azure Speech key, region, and optionally Azure OpenAI credentials

# CLI demos
cd HelloComputer
dotnet restore
dotnet run -- stt
dotnet run -- stt --file samples/sample_english.wav
dotnet run -- tts --text "Hello, Computer!"
dotnet run -- tts --text "Hello, Computer!" --voice en-US-AmandaMultilingualNeural

# Web application (Speech-to-Text, Text-to-Speech, Translation,
# Pronunciation Assessment, Chat with AI)
cd ../HelloComputer.Web
dotnet restore
dotnet run
```

### Voices

Microsoft has [a series of voices available](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts) for text to speech. The examples above show two and the code defaults to `en-US-JennyNeural`.

### Browser Microphone Note

The .NET web app and Python Streamlit pages capture mic audio directly in the browser. Browsers only allow `getUserMedia` on `localhost` or over HTTPS -- if you present from a remote URL, terminate TLS in front of the app.
