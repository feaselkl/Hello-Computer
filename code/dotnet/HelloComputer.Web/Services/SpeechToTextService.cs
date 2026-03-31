using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

namespace HelloComputer.Web.Services;

public static class SpeechToTextService
{
    public static async Task<string> FromWavBytes(byte[] wavBytes)
    {
        var config = SpeechHelper.GetSpeechConfig();

        using var stream = AudioInputStream.CreatePushStream(
            AudioStreamFormat.GetWaveFormatPCM(16000, 16, 1));
        stream.Write(wavBytes);
        stream.Close();

        using var audioConfig = AudioConfig.FromStreamInput(stream);
        using var recognizer = new SpeechRecognizer(config, audioConfig);

        var result = await recognizer.RecognizeOnceAsync();

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
