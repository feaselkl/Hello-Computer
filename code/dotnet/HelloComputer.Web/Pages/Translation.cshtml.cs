using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using HelloComputer.Web.Services;

namespace HelloComputer.Web.Pages;

public class TranslationModel : PageModel
{
    public List<(string Label, string Code)> SourceLanguages { get; } =
    [
        ("English (US)", "en-US"),
        ("Mandarin Chinese", "zh-CN"),
        ("Spanish (Spain)", "es-ES"),
        ("French (France)", "fr-FR"),
        ("German", "de-DE"),
        ("Italian", "it-IT"),
        ("Japanese", "ja-JP"),
        ("Korean", "ko-KR"),
        ("Portuguese (Brazil)", "pt-BR"),
        ("Russian", "ru-RU"),
        ("Arabic (Saudi Arabia)", "ar-SA"),
        ("Hindi", "hi-IN"),
    ];

    public List<(string Label, string Code)> TargetLanguagesCatalog { get; } =
    [
        ("English", "en"),
        ("Chinese (Simplified)", "zh-Hans"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de"),
        ("Italian", "it"),
        ("Japanese", "ja"),
        ("Korean", "ko"),
        ("Portuguese", "pt"),
        ("Russian", "ru"),
        ("Arabic", "ar"),
        ("Hindi", "hi"),
    ];

    public string SourceLanguage { get; set; } = "zh-CN";
    public List<string> TargetLanguages { get; set; } = ["en"];
    public bool SpeakTranslation { get; set; }

    public string? RecognizedText { get; set; }
    public Dictionary<string, string> Translations { get; set; } = new();
    public Dictionary<string, string> TranslationAudio { get; set; } = new();
    public string? Error { get; set; }

    public async Task<IActionResult> OnPostAsync(
        IFormFile? wavFile,
        string sourceLanguage,
        string[] targetLanguages,
        bool speakTranslation)
    {
        SourceLanguage = sourceLanguage;
        TargetLanguages = targetLanguages?.ToList() ?? [];
        SpeakTranslation = speakTranslation;

        if (wavFile == null || wavFile.Length == 0)
        {
            Error = "Please select a WAV file.";
            return Page();
        }

        if (TargetLanguages.Count == 0)
        {
            Error = "Select at least one target language.";
            return Page();
        }

        try
        {
            using var ms = new MemoryStream();
            await wavFile.CopyToAsync(ms);
            var outcome = await TranslationService.FromWavBytes(
                ms.ToArray(), SourceLanguage, TargetLanguages);

            RecognizedText = outcome.RecognizedText;
            Translations = outcome.Translations;

            if (SpeakTranslation)
            {
                foreach (var pair in Translations)
                {
                    if (!TranslationService.DefaultTargetVoices.TryGetValue(pair.Key, out var voice))
                        continue;
                    try
                    {
                        var audio = await TextToSpeechService.SynthesizeToBytes(pair.Value, voice);
                        TranslationAudio[pair.Key] = Convert.ToBase64String(audio);
                    }
                    catch
                    {
                        // Skip synthesis errors; translation text still displays.
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Error = ex.Message;
        }

        return Page();
    }
}
