using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

namespace HelloComputer;

public static class TextToSpeech
{
    public static async Task SpeakAsync(
        string text, string voiceName = "en-US-JennyNeural", string? endpointId = null)
    {
        var config = SpeechHelper.GetSpeechConfig();
        ConfigureVoice(config, voiceName, endpointId);

        using var audioConfig = AudioConfig.FromDefaultSpeakerOutput();
        using var synthesizer = new SpeechSynthesizer(config, audioConfig);

        var result = await synthesizer.SpeakTextAsync(text);
        HandleResult(result);
    }

    public static async Task SynthesizeToWavAsync(
        string text, string outputPath, string voiceName = "en-US-JennyNeural",
        string? endpointId = null)
    {
        var config = SpeechHelper.GetSpeechConfig();
        ConfigureVoice(config, voiceName, endpointId);

        using var audioConfig = AudioConfig.FromWavFileOutput(outputPath);
        using var synthesizer = new SpeechSynthesizer(config, audioConfig);

        var result = await synthesizer.SpeakTextAsync(text);
        HandleResult(result);
    }

    public static async Task ListVoicesAsync(string locale = "en-US")
    {
        var config = SpeechHelper.GetSpeechConfig();
        using var synthesizer = new SpeechSynthesizer(config, null as AudioConfig);

        var voicesResult = await synthesizer.GetVoicesAsync(locale);
        if (voicesResult.Reason == ResultReason.VoicesListRetrieved)
        {
            Console.WriteLine($"Available voices for {locale}:");
            Console.WriteLine();
            foreach (var voice in voicesResult.Voices)
            {
                Console.WriteLine($"  {voice.ShortName,-30} {voice.LocalName,-20} {voice.Gender}");
            }
        }
        else
        {
            throw new InvalidOperationException($"Failed to list voices: {voicesResult.Reason}");
        }
    }

    private static void ConfigureVoice(
        SpeechConfig config, string voiceName, string? endpointId)
    {
        var resolvedEndpoint = endpointId
            ?? Environment.GetEnvironmentVariable("AZURE_SPEECH_ENDPOINT_ID");

        if (!string.IsNullOrEmpty(resolvedEndpoint))
            config.EndpointId = resolvedEndpoint;

        config.SpeechSynthesisVoiceName = voiceName;
    }

    private static void HandleResult(SpeechSynthesisResult result)
    {
        if (result.Reason == ResultReason.SynthesizingAudioCompleted)
            return;

        if (result.Reason == ResultReason.Canceled)
        {
            var details = SpeechSynthesisCancellationDetails.FromResult(result);
            var msg = $"Synthesis canceled: {details.Reason}";
            if (!string.IsNullOrEmpty(details.ErrorDetails))
                msg += $" -- {details.ErrorDetails}";
            throw new InvalidOperationException(msg);
        }

        throw new InvalidOperationException($"Unexpected synthesis result: {result.Reason}");
    }
}
