# Hello, Computer -- .NET Demos

Azure Speech demos for the "Hello, Computer: An Introduction to Azure Speech" presentation.

## Prerequisites

- .NET 9.0 SDK or later
- An Azure Speech resource ([create one here](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices))
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

The CLI covers speech-to-text, text-to-speech, and voice listing. Translation and pronunciation assessment are demonstrated through the web application.

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

A Razor Pages web application that mirrors the Python Streamlit dashboard:

- **Speech to Text** -- record from the browser microphone or upload a WAV file to transcribe
- **Text to Speech** -- type text, choose a voice, and play the synthesized audio
- **Translation** -- record or upload WAV audio and translate into one or more target languages, optionally speaking the translations back
- **Pronunciation Assessment** -- read a reference sentence and get a score breakdown with word-by-word error tracking
- **Chat with AI** -- type a message, send it to a language model, and hear the response

```bash
cd HelloComputer.Web
dotnet run
```

Then open the URL shown in the terminal (typically `http://localhost:5000`).

### Browser microphone

The Speech to Text, Translation, and Pronunciation Assessment pages record audio directly in the browser. Under the hood, [wwwroot/js/mic-recorder.js](HelloComputer.Web/wwwroot/js/mic-recorder.js) uses the Web Audio API to capture 16 kHz PCM and encodes a WAV blob client-side, then injects it into the existing file input via `DataTransfer`. Servers are identical to the upload path -- no additional native dependencies (like GStreamer) are needed.

Browsers only allow `getUserMedia` on `localhost` or over HTTPS. If you present from a remote URL, terminate TLS in front of the app.

### Notes on specific pages

**Translation:** the source language defaults to Mandarin and the target to English, matching the slide deck. Select multiple target languages with Ctrl/Cmd-click. When "Also speak the translation" is checked, each translation is synthesized with a default neural voice for the target language.

**Pronunciation Assessment:** reference sentences are loaded from [code/samples/pronunciation_inputs.yaml](../samples/pronunciation_inputs.yaml), which is the same file the Python demo reads. The sample dropdown auto-submits to populate the reference text; pick "-- Custom text --" to enter your own. The results show pronunciation, accuracy, fluency, completeness, and prosody scores (prosody is en-US only), a color-coded word-by-word breakdown (good / fair / poor / omission / insertion / break issue), an error summary, a phoneme-level expander, and the raw Azure JSON response.

## Project Structure

```
code/dotnet/
  .env.example                            Template for Azure credentials
  README.md                               This file
  HelloComputer/
    HelloComputer.csproj                  CLI project file
    Program.cs                            CLI entry point and argument parsing
    SpeechConfig.cs                       Azure SDK configuration from env vars
    SpeechToText.cs                       Speech-to-text (microphone and WAV file)
    TextToSpeech.cs                       Text-to-speech (speaker, WAV file, voice listing)
  HelloComputer.Web/
    HelloComputer.Web.csproj              Web project file with NuGet dependencies
    Program.cs                            Web application entry point
    wwwroot/
      js/mic-recorder.js                  Browser mic -> WAV recorder (shared by mic-capable pages)
    Services/
      SpeechHelper.cs                     Azure SDK configuration from env vars
      SpeechToTextService.cs              Speech-to-text from WAV bytes
      TextToSpeechService.cs              Text-to-speech (synthesis, voice listing)
      TranslationService.cs               Translation from WAV bytes, default target voices
      PronunciationAssessmentService.cs   Pronunciation scoring + JSON parsing
      PronunciationSamples.cs             YAML loader for shared reference samples
      ChatService.cs                      Azure OpenAI chat completions
    Pages/
      Index.cshtml                        Home page with navigation links
      SpeechToText.cshtml                 STT demo page (mic + WAV)
      TextToSpeech.cshtml                 TTS demo page
      Translation.cshtml                  Translation demo page (mic + WAV)
      PronunciationAssessment.cshtml      Pronunciation demo page (mic + WAV)
      Chat.cshtml                         Chat with AI demo page
      Shared/_Layout.cshtml               Layout and navigation
```

Reference samples used by the pronunciation page live at `../samples/pronunciation_inputs.yaml` relative to this directory.
