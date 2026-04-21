using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using HelloComputer.Web.Services;

namespace HelloComputer.Web.Pages;

public class PronunciationAssessmentModel : PageModel
{
    public const string CustomOption = "-- Custom text --";

    public static readonly string[] SupportedLanguages =
        ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "ja-JP", "zh-CN"];

    public List<PronunciationSample> Samples { get; set; } = [];
    public string SelectedTitle { get; set; } = "";
    public string ReferenceText { get; set; } = "";
    public string Language { get; set; } = "en-US";

    public AssessmentOutcome? Outcome { get; set; }
    public string? Error { get; set; }

    public void OnGet()
    {
        Samples = PronunciationSamples.Load();
        if (Samples.Count > 0)
        {
            SelectedTitle = Samples[0].Title;
            ReferenceText = Samples[0].Text;
            Language = Samples[0].Language;
        }
        else
        {
            SelectedTitle = CustomOption;
            ReferenceText = "Hello, computer.";
        }
    }

    public async Task<IActionResult> OnPostAsync(
        IFormFile? wavFile,
        string? sampleTitle,
        string? referenceText,
        string? language,
        string? action)
    {
        Samples = PronunciationSamples.Load();
        SelectedTitle = sampleTitle ?? "";

        // Sample-swap: repopulate from the chosen sample unless the user picked Custom.
        if (!string.IsNullOrEmpty(SelectedTitle) && SelectedTitle != CustomOption)
        {
            var match = Samples.FirstOrDefault(s => s.Title == SelectedTitle);
            if (match != null)
            {
                ReferenceText = match.Text;
                Language = match.Language;
            }
        }
        else
        {
            ReferenceText = referenceText ?? "";
            Language = language ?? "en-US";
        }

        if (action != "assess")
        {
            // User just switched samples; re-render without running assessment.
            return Page();
        }

        if (wavFile == null || wavFile.Length == 0)
        {
            Error = "Please record audio or upload a WAV file.";
            return Page();
        }
        if (string.IsNullOrWhiteSpace(ReferenceText))
        {
            Error = "Reference text is required.";
            return Page();
        }

        try
        {
            using var ms = new MemoryStream();
            await wavFile.CopyToAsync(ms);
            Outcome = await PronunciationAssessmentService.FromWavBytes(
                ms.ToArray(), ReferenceText, Language);
        }
        catch (Exception ex)
        {
            Error = ex.Message;
        }

        return Page();
    }

    public static string ScoreColor(double? score) => score switch
    {
        null => "#e2e3e5",
        >= 80 => "#d4edda",
        >= 60 => "#fff3cd",
        _ => "#f8d7da",
    };

    public static string WordBackground(WordAssessment w)
    {
        return w.ErrorType switch
        {
            "Omission" or "Insertion" => "#f5c2c7",
            "UnexpectedBreak" or "MissingBreak" => "#ffe5b4",
            "Monotone" => "#e2e3e5",
            "Mispronunciation" => "#fff3cd",
            _ => ScoreColor(w.AccuracyScore),
        };
    }
}
