using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

namespace HelloComputer;

public static class SpeechToText
{
    public static async Task<string> FromMicrophoneAsync()
    {
        var config = SpeechHelper.GetSpeechConfig();
        using var audioConfig = AudioConfig.FromDefaultMicrophoneInput();
        using var recognizer = new SpeechRecognizer(config, audioConfig);

        var result = await recognizer.RecognizeOnceAsync();
        return HandleResult(result);
    }

    public static async Task<string> FromWavFileAsync(string filePath)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException($"WAV file not found: {filePath}");

        var config = SpeechHelper.GetSpeechConfig();
        using var audioConfig = AudioConfig.FromWavFileInput(filePath);
        using var recognizer = new SpeechRecognizer(config, audioConfig);

        var result = await recognizer.RecognizeOnceAsync();
        return HandleResult(result);
    }

    private static string HandleResult(SpeechRecognitionResult result)
    {
        return result.Reason switch
        {
            ResultReason.RecognizedSpeech => result.Text,
            ResultReason.NoMatch => throw new InvalidOperationException(
                "No speech recognized. Check your audio input."),
            ResultReason.Canceled => throw new InvalidOperationException(
                FormatCancellation(CancellationDetails.FromResult(result))),
            _ => throw new InvalidOperationException(
                $"Unexpected result: {result.Reason}")
        };
    }

    private static string FormatCancellation(CancellationDetails details)
    {
        var msg = $"Recognition canceled: {details.Reason}";
        if (!string.IsNullOrEmpty(details.ErrorDetails))
            msg += $" -- {details.ErrorDetails}";
        return msg;
    }
}
