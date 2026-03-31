# Hello, Computer -- .NET Demos

Azure AI Speech demos for the "Hello, Computer: An Introduction to Azure Speech" presentation.

## Prerequisites

- .NET 9.0 SDK or later
- An Azure AI Speech resource ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices))
- For microphone demos: a working system microphone
- On Linux: `sudo apt-get install libssl-dev libasound2-dev` (required by the Azure Speech SDK)

## Setup

```bash
cd code/dotnet/HelloComputer

# Create your .env file with your Azure credentials
cp ../.env.example .env
# Edit .env -- set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION

# Restore packages
dotnet restore
```

## Usage

### Speech-to-text from your microphone

```bash
dotnet run -- stt
```

### Speech-to-text from a WAV file

```bash
dotnet run -- stt --file path/to/audio.wav
```

### Text-to-speech (plays through your speaker)

```bash
dotnet run -- tts --text "Hello, Computer!"
```

### Text-to-speech saved to a WAV file

```bash
dotnet run -- tts --text "Hello, Computer!" --output hello.wav
```

### Text-to-speech with a specific voice

```bash
dotnet run -- tts --text "Hello, Computer!" --voice en-US-GuyNeural
```

### List available voices

```bash
dotnet run -- voices
dotnet run -- voices --locale en-GB
```

## Project Structure

```
code/dotnet/
  .env.example                   Template for Azure credentials
  README.md                      This file
  HelloComputer/
    HelloComputer.csproj         Project file with NuGet dependencies
    Program.cs                   CLI entry point and argument parsing
    SpeechConfig.cs              Azure SDK configuration from env vars
    SpeechToText.cs              Speech-to-text (microphone and WAV file)
    TextToSpeech.cs              Text-to-speech (speaker, WAV file, voice listing)
```
