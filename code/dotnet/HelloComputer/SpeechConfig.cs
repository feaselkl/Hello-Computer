using Microsoft.CognitiveServices.Speech;

namespace HelloComputer;

public static class SpeechHelper
{
    public static SpeechConfig GetSpeechConfig()
    {
        DotNetEnv.Env.TraversePath().Load();

        var key = Environment.GetEnvironmentVariable("AZURE_SPEECH_KEY");
        var region = Environment.GetEnvironmentVariable("AZURE_SPEECH_REGION");

        if (string.IsNullOrEmpty(key) || string.IsNullOrEmpty(region))
        {
            throw new InvalidOperationException(
                "Missing environment variables. " +
                "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION " +
                "(or create a .env file from .env.example).");
        }

        return Microsoft.CognitiveServices.Speech.SpeechConfig.FromSubscription(key, region);
    }
}
