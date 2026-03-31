# Hello, Computer: An Introduction to Azure Speech

This repository provides the supporting code for my presentation entitled [Hello, Computer: An Introduction to Azure Speech](https://www.catallaxyservices.com/presentations/hello-computer/).

## Running the Code

There are two sets of demos in this repository: one in Python and one in .NET.

### Python Demos

See [code/python/README.md](code/python/README.md) for setup and usage instructions. The Python demos include a CLI tool and a Streamlit dashboard for speech-to-text, text-to-speech, and a voice chat demo that connects speech to an Azure AI Foundry language model.

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), an Azure AI Speech resource. For the Chat with AI demo: an Azure OpenAI deployment.

```bash
cd code/python
cp .env.example .env
# Edit .env with your Azure Speech key and region
uv sync
uv run python cli.py stt
uv run python cli.py tts --text "This is a test of text to speech."
uv run python cli.py tts --text "This is a test of text to speech." --voice en-US-Phoebe:DragonHDLatestNeural
uv run streamlit run app.py
```

### .NET Demos

See [code/dotnet/README.md](code/dotnet/README.md) for setup and usage instructions. The .NET demos include a CLI tool for speech-to-text, text-to-speech, and voice listing.

**Requirements:** .NET 9.0 SDK, an Azure AI Speech resource.

```bash
cd code/dotnet/HelloComputer
cp ../.env.example .env
# Edit .env with your Azure Speech key and region
dotnet restore
dotnet run -- stt
dotnet run -- tts --text "Hello, Computer!"
dotnet run -- tts --text "Hello, Computer!" --voice en-US-AmandaMultilingualNeural
```

### Voices

Microsoft has [a series of voices available](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts) for text to speech. The examples above show two and the code defaults to en-US-JennyNeural.
