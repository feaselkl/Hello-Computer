namespace HelloComputer;

class Program
{
    static async Task<int> Main(string[] args)
    {
        if (args.Length == 0)
        {
            PrintUsage();
            return 1;
        }

        try
        {
            switch (args[0].ToLowerInvariant())
            {
                case "stt":
                    await RunSttAsync(args[1..]);
                    break;
                case "tts":
                    await RunTtsAsync(args[1..]);
                    break;
                case "voices":
                    var locale = GetOption(args[1..], "--locale") ?? "en-US";
                    await TextToSpeech.ListVoicesAsync(locale);
                    break;
                case "help":
                case "--help":
                case "-h":
                    PrintUsage();
                    break;
                default:
                    Console.Error.WriteLine($"Unknown command: {args[0]}");
                    PrintUsage();
                    return 1;
            }
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error: {ex.Message}");
            return 1;
        }
    }

    private static async Task RunSttAsync(string[] args)
    {
        var filePath = GetOption(args, "--file") ?? GetOption(args, "-f");

        if (filePath is not null)
        {
            Console.WriteLine($"Transcribing from {filePath} ...");
            var text = await SpeechToText.FromWavFileAsync(filePath);
            Console.WriteLine();
            Console.WriteLine($"Recognized: {text}");
        }
        else
        {
            Console.WriteLine("Listening on your microphone (speak now) ...");
            var text = await SpeechToText.FromMicrophoneAsync();
            Console.WriteLine();
            Console.WriteLine($"Recognized: {text}");
        }
    }

    private static async Task RunTtsAsync(string[] args)
    {
        var text = GetOption(args, "--text") ?? GetOption(args, "-t");
        if (text is null)
        {
            Console.Error.WriteLine("Error: --text is required for tts command.");
            return;
        }

        var voice = GetOption(args, "--voice") ?? GetOption(args, "-v") ?? "en-US-JennyNeural";
        var output = GetOption(args, "--output") ?? GetOption(args, "-o");
        var speakerProfileId = GetOption(args, "--speaker-profile-id") ?? GetOption(args, "-s");

        if (output is not null)
        {
            Console.WriteLine($"Synthesizing to {output} ...");
            await TextToSpeech.SynthesizeToWavAsync(text, output, voice, speakerProfileId);
            Console.WriteLine($"Saved to {output}");
        }
        else
        {
            Console.WriteLine("Speaking ...");
            await TextToSpeech.SpeakAsync(text, voice, speakerProfileId);
            Console.WriteLine("Done.");
        }
    }

    private static string? GetOption(string[] args, string name)
    {
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == name)
                return args[i + 1];
        }
        return null;
    }

    private static void PrintUsage()
    {
        Console.WriteLine("""
            Hello, Computer -- Azure AI Speech CLI (.NET)

            Usage:
              dotnet run -- stt [--file <path.wav>]
              dotnet run -- tts --text "Hello" [--output <path.wav>] [--voice <name>]
                               [--speaker-profile-id <id>]
              dotnet run -- voices [--locale <locale>]

            Commands:
              stt       Speech-to-text (default: microphone, or --file for WAV)
              tts       Text-to-speech (--text required; plays speaker or saves to --output)
              voices    List available neural voices for a locale (default: en-US)

            Options:
              --speaker-profile-id   Personal Voice speaker profile ID
                                     (or set AZURE_SPEECH_SPEAKER_PROFILE_ID env var)

            Environment:
              AZURE_SPEECH_KEY                  Your Azure Speech subscription key
              AZURE_SPEECH_REGION               Your Azure Speech region (e.g., eastus)
              AZURE_SPEECH_SPEAKER_PROFILE_ID   Personal Voice speaker profile ID (optional)

              Set these in environment variables or in a .env file.
            """);
    }
}
