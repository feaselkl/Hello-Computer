using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

namespace HelloComputer;

public static class TextToSpeech
{
    public static async Task SpeakAsync(
        string text, string voiceName = "en-US-JennyNeural", string? speakerProfileId = null)
    {
        var config = SpeechHelper.GetSpeechConfig();
        speakerProfileId ??= Environment.GetEnvironmentVariable("AZURE_SPEECH_SPEAKER_PROFILE_ID");

        SpeechSynthesisResult result;
        if (!string.IsNullOrEmpty(speakerProfileId))
        {
            using var audioConfig = AudioConfig.FromDefaultSpeakerOutput();
            using var synthesizer = new SpeechSynthesizer(config, audioConfig);
            var ssml = BuildPersonalVoiceSsml(text, speakerProfileId, voiceName);
            result = await synthesizer.SpeakSsmlAsync(ssml);
        }
        else
        {
            config.SpeechSynthesisVoiceName = voiceName;
            using var audioConfig = AudioConfig.FromDefaultSpeakerOutput();
            using var synthesizer = new SpeechSynthesizer(config, audioConfig);
            result = await synthesizer.SpeakTextAsync(text);
        }
        HandleResult(result);
    }

    public static async Task SynthesizeToWavAsync(
        string text, string outputPath, string voiceName = "en-US-JennyNeural",
        string? speakerProfileId = null)
    {
        var config = SpeechHelper.GetSpeechConfig();
        speakerProfileId ??= Environment.GetEnvironmentVariable("AZURE_SPEECH_SPEAKER_PROFILE_ID");

        SpeechSynthesisResult result;
        if (!string.IsNullOrEmpty(speakerProfileId))
        {
            using var audioConfig = AudioConfig.FromWavFileOutput(outputPath);
            using var synthesizer = new SpeechSynthesizer(config, audioConfig);
            var ssml = BuildPersonalVoiceSsml(text, speakerProfileId, voiceName);
            result = await synthesizer.SpeakSsmlAsync(ssml);
        }
        else
        {
            config.SpeechSynthesisVoiceName = voiceName;
            using var audioConfig = AudioConfig.FromWavFileOutput(outputPath);
            using var synthesizer = new SpeechSynthesizer(config, audioConfig);
            result = await synthesizer.SpeakTextAsync(text);
        }
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

    private static string BuildPersonalVoiceSsml(
        string text, string speakerProfileId, string voiceName = "DragonLatestNeural")
    {
        var escaped = System.Security.SecurityElement.Escape(text);
        return "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
             + "xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>"
             + $"<voice name='{voiceName}'>"
             + $"<mstts:ttsembedding speakerProfileId='{speakerProfileId}'>"
             + escaped
             + "</mstts:ttsembedding>"
             + "</voice>"
             + "</speak>";
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
