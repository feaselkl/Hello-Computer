using Microsoft.CognitiveServices.Speech;

namespace HelloComputer.Web.Services;

public static class SpeechHelper
{
    public static SpeechConfig GetSpeechConfig()
    {
        var key = Environment.GetEnvironmentVariable("AZURE_SPEECH_KEY");
        var region = Environment.GetEnvironmentVariable("AZURE_SPEECH_REGION");

        if (string.IsNullOrEmpty(key) || string.IsNullOrEmpty(region))
        {
            throw new InvalidOperationException(
                "Missing environment variables. " +
                "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION " +
                "(or create a .env file from .env.example).");
        }

        return SpeechConfig.FromSubscription(key, region);
    }

    public static string? GetSpeakerProfileId()
    {
        var id = Environment.GetEnvironmentVariable("AZURE_SPEECH_SPEAKER_PROFILE_ID");
        return string.IsNullOrWhiteSpace(id) ? null : id;
    }
}
