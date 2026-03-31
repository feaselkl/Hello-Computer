# Hello, Computer -- .NET Demos

Azure AI Speech demos for the "Hello, Computer: An Introduction to Azure Speech" presentation.

## Prerequisites

- .NET 9.0 SDK or later
- An Azure AI Speech resource ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices))
- For the Chat with AI demo: an Azure OpenAI deployment ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI))
- For microphone demos: a working system microphone
- On Linux: `sudo apt-get install libssl-dev libasound2-dev` (required by the Azure Speech SDK)

## Setup

```bash
cd code/dotnet

# Create your .env file with your Azure credentials
cp .env.example .env
# Edit .env -- set AZURE_SPEECH_KEY, AZURE_SPEECH_REGION,
# and optionally AZURE_OPENAI_* variables for the Chat with AI demo
```

## CLI Usage

### Speech-to-text from your microphone

```bash
cd HelloComputer
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

### Text-to-speech with a Personal Voice

```bash
dotnet run -- tts --text "Hello, Computer!" --speaker-profile-id <your-profile-id>
```

You can also set `AZURE_SPEECH_SPEAKER_PROFILE_ID` in your `.env` file instead of passing the flag each time.

### List available voices

```bash
dotnet run -- voices
dotnet run -- voices --locale en-GB
```

## Web Application

A Razor Pages web application that provides the same three demos as the Python Streamlit dashboard:

- **Speech to Text** -- upload a WAV file to transcribe
- **Text to Speech** -- type text, choose a voice, and play the synthesized audio
- **Chat with AI** -- type a message, send it to a language model, and hear the response

```bash
cd HelloComputer.Web
dotnet run
```

Then open the URL shown in the terminal (typically `http://localhost:5000`).

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
  HelloComputer.Web/
    HelloComputer.Web.csproj     Web project file with NuGet dependencies
    Program.cs                   Web application entry point
    Services/
      SpeechHelper.cs            Azure SDK configuration from env vars
      SpeechToTextService.cs     Speech-to-text from WAV bytes
      TextToSpeechService.cs     Text-to-speech (synthesis, voice listing)
      ChatService.cs             Azure OpenAI chat completions
    Pages/
      Index.cshtml               Home page with navigation links
      SpeechToText.cshtml        STT demo page (WAV file upload)
      TextToSpeech.cshtml        TTS demo page (voice selection, synthesis)
      Chat.cshtml                STT -> LLM -> TTS demo page
```
