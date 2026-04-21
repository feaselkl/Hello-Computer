using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.CognitiveServices.Speech.Translation;

namespace HelloComputer.Web.Services;

public static class TranslationService
{
    public static async Task<TranslationOutcome> FromWavBytes(
        byte[] wavBytes,
        string sourceLanguage,
        IEnumerable<string> targetLanguages)
    {
        var config = GetTranslationConfig(sourceLanguage, targetLanguages);

        using var stream = AudioInputStream.CreatePushStream(
            AudioStreamFormat.GetWaveFormatPCM(16000, 16, 1));
        stream.Write(wavBytes);
        stream.Close();

        using var audioConfig = AudioConfig.FromStreamInput(stream);
        using var recognizer = new TranslationRecognizer(config, audioConfig);

        var result = await recognizer.RecognizeOnceAsync();

        return result.Reason switch
        {
            ResultReason.TranslatedSpeech =>
                new TranslationOutcome(result.Text, result.Translations.ToDictionary(kv => kv.Key, kv => kv.Value)),
            ResultReason.RecognizedSpeech =>
                new TranslationOutcome(result.Text, new Dictionary<string, string>()),
            ResultReason.NoMatch => throw new InvalidOperationException(
                "No speech recognized. Check your audio input and source language."),
            ResultReason.Canceled => throw new InvalidOperationException(
                FormatCancellation(CancellationDetails.FromResult(result))),
            _ => throw new InvalidOperationException(
                $"Unexpected result: {result.Reason}")
        };
    }

    private static SpeechTranslationConfig GetTranslationConfig(
        string sourceLanguage,
        IEnumerable<string> targetLanguages)
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

        var config = SpeechTranslationConfig.FromSubscription(key, region);
        config.SpeechRecognitionLanguage = sourceLanguage;
        foreach (var lang in targetLanguages)
            config.AddTargetLanguage(lang);
        return config;
    }

    private static string FormatCancellation(CancellationDetails details)
    {
        var msg = $"Translation canceled: {details.Reason}";
        if (!string.IsNullOrEmpty(details.ErrorDetails))
            msg += $" -- {details.ErrorDetails}";
        return msg;
    }

    // Default neural voices for synthesizing translated text, keyed by the
    // target language code supplied to AddTargetLanguage.
    public static readonly Dictionary<string, string> DefaultTargetVoices = new()
    {
        ["en"] = "en-US-JennyNeural",
        ["es"] = "es-ES-ElviraNeural",
        ["fr"] = "fr-FR-DeniseNeural",
        ["de"] = "de-DE-KatjaNeural",
        ["it"] = "it-IT-ElsaNeural",
        ["pt"] = "pt-BR-FranciscaNeural",
        ["zh-Hans"] = "zh-CN-XiaoxiaoNeural",
        ["ja"] = "ja-JP-NanamiNeural",
        ["ko"] = "ko-KR-SunHiNeural",
        ["ru"] = "ru-RU-SvetlanaNeural",
        ["ar"] = "ar-SA-ZariyahNeural",
        ["hi"] = "hi-IN-SwaraNeural",
    };
}

public record TranslationOutcome(string RecognizedText, Dictionary<string, string> Translations);
