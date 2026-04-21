using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using Microsoft.CognitiveServices.Speech.PronunciationAssessment;

namespace HelloComputer.Web.Services;

public static class PronunciationAssessmentService
{
    public static async Task<AssessmentOutcome> FromWavBytes(
        byte[] wavBytes, string referenceText, string language)
    {
        var speechConfig = SpeechHelper.GetSpeechConfig();
        speechConfig.SpeechRecognitionLanguage = language;

        var pronConfig = new PronunciationAssessmentConfig(
            referenceText,
            GradingSystem.HundredMark,
            Granularity.Phoneme,
            enableMiscue: true);
        if (language.StartsWith("en-", StringComparison.OrdinalIgnoreCase))
        {
            pronConfig.EnableProsodyAssessment();
        }

        using var stream = AudioInputStream.CreatePushStream(
            AudioStreamFormat.GetWaveFormatPCM(16000, 16, 1));
        stream.Write(wavBytes);
        stream.Close();

        using var audioConfig = AudioConfig.FromStreamInput(stream);
        using var recognizer = new SpeechRecognizer(speechConfig, audioConfig);
        pronConfig.ApplyTo(recognizer);

        var result = await recognizer.RecognizeOnceAsync();

        return result.Reason switch
        {
            ResultReason.RecognizedSpeech => Parse(result),
            ResultReason.NoMatch => throw new InvalidOperationException(
                "No speech recognized. Check your audio input."),
            ResultReason.Canceled => throw new InvalidOperationException(
                FormatCancellation(CancellationDetails.FromResult(result))),
            _ => throw new InvalidOperationException(
                $"Unexpected result: {result.Reason}")
        };
    }

    private static AssessmentOutcome Parse(SpeechRecognitionResult result)
    {
        var json = result.Properties.GetProperty(PropertyId.SpeechServiceResponse_JsonResult);
        if (string.IsNullOrEmpty(json))
        {
            return new AssessmentOutcome(result.Text, null, null, null, null, null, [], "{}");
        }

        // Parse with a DOM reader so we don't break if Azure adds fields.
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        var displayText = root.TryGetProperty("DisplayText", out var dt) ? dt.GetString() ?? result.Text : result.Text;

        double? pron = null, acc = null, flu = null, comp = null, pros = null;
        var words = new List<WordAssessment>();

        if (root.TryGetProperty("NBest", out var nbest) && nbest.ValueKind == JsonValueKind.Array && nbest.GetArrayLength() > 0)
        {
            var first = nbest[0];
            if (first.TryGetProperty("PronunciationAssessment", out var scores))
            {
                pron = ReadDouble(scores, "PronScore");
                acc = ReadDouble(scores, "AccuracyScore");
                flu = ReadDouble(scores, "FluencyScore");
                comp = ReadDouble(scores, "CompletenessScore");
                pros = ReadDouble(scores, "ProsodyScore");
            }
            if (first.TryGetProperty("Words", out var wordArr) && wordArr.ValueKind == JsonValueKind.Array)
            {
                foreach (var w in wordArr.EnumerateArray())
                    words.Add(ParseWord(w));
            }
        }

        return new AssessmentOutcome(displayText, pron, acc, flu, comp, pros, words, json);
    }

    private static WordAssessment ParseWord(JsonElement w)
    {
        var word = w.TryGetProperty("Word", out var wv) ? wv.GetString() ?? "" : "";
        double? accuracy = null;
        string errorType = "None";
        if (w.TryGetProperty("PronunciationAssessment", out var pa))
        {
            accuracy = ReadDouble(pa, "AccuracyScore");
            if (pa.TryGetProperty("ErrorType", out var et))
                errorType = et.GetString() ?? "None";
        }

        var phonemes = new List<PhonemeAssessment>();
        if (w.TryGetProperty("Phonemes", out var pArr) && pArr.ValueKind == JsonValueKind.Array)
        {
            foreach (var p in pArr.EnumerateArray())
            {
                var ph = p.TryGetProperty("Phoneme", out var pv) ? pv.GetString() ?? "" : "";
                double? pscore = null;
                if (p.TryGetProperty("PronunciationAssessment", out var ppa))
                    pscore = ReadDouble(ppa, "AccuracyScore");
                phonemes.Add(new PhonemeAssessment(ph, pscore));
            }
        }

        return new WordAssessment(word, accuracy, errorType, phonemes);
    }

    private static double? ReadDouble(JsonElement parent, string name)
    {
        if (!parent.TryGetProperty(name, out var v)) return null;
        return v.ValueKind switch
        {
            JsonValueKind.Number => v.GetDouble(),
            JsonValueKind.String when double.TryParse(v.GetString(), out var d) => d,
            _ => null,
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

public record AssessmentOutcome(
    string RecognizedText,
    double? PronunciationScore,
    double? AccuracyScore,
    double? FluencyScore,
    double? CompletenessScore,
    double? ProsodyScore,
    List<WordAssessment> Words,
    string RawJson);

public record WordAssessment(
    string Word,
    double? AccuracyScore,
    string ErrorType,
    List<PhonemeAssessment> Phonemes);

public record PhonemeAssessment(string Phoneme, double? AccuracyScore);
