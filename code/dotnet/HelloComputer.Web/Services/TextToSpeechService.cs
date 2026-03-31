using Microsoft.CognitiveServices.Speech;

namespace HelloComputer.Web.Services;

public static class TextToSpeechService
{
    public static async Task<byte[]> SynthesizeToBytes(
        string text, string voiceName = "en-US-JennyNeural", string? speakerProfileId = null)
    {
        var config = SpeechHelper.GetSpeechConfig();
        speakerProfileId ??= SpeechHelper.GetSpeakerProfileId();

        SpeechSynthesisResult result;
        if (!string.IsNullOrEmpty(speakerProfileId))
        {
            using var synthesizer = new SpeechSynthesizer(config, null as Microsoft.CognitiveServices.Speech.Audio.AudioConfig);
            var ssml = BuildPersonalVoiceSsml(text, speakerProfileId, voiceName);
            result = await synthesizer.SpeakSsmlAsync(ssml);
        }
        else
        {
            config.SpeechSynthesisVoiceName = voiceName;
            using var synthesizer = new SpeechSynthesizer(config, null as Microsoft.CognitiveServices.Speech.Audio.AudioConfig);
            result = await synthesizer.SpeakTextAsync(text);
        }

        if (result.Reason == ResultReason.Canceled)
        {
            var details = SpeechSynthesisCancellationDetails.FromResult(result);
            var msg = $"Synthesis canceled: {details.Reason}";
            if (!string.IsNullOrEmpty(details.ErrorDetails))
                msg += $" -- {details.ErrorDetails}";
            throw new InvalidOperationException(msg);
        }

        return result.AudioData;
    }

    public static async Task<List<VoiceInfo>> ListVoicesAsync(string locale = "en-US")
    {
        var config = SpeechHelper.GetSpeechConfig();
        using var synthesizer = new SpeechSynthesizer(config, null as Microsoft.CognitiveServices.Speech.Audio.AudioConfig);

        var voicesResult = await synthesizer.GetVoicesAsync(locale);
        if (voicesResult.Reason == ResultReason.VoicesListRetrieved)
            return [.. voicesResult.Voices];

        throw new InvalidOperationException($"Failed to list voices: {voicesResult.Reason}");
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
}

public record VoiceOption(string Name, string LocalName, string Gender);
