using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using HelloComputer.Web.Services;

namespace HelloComputer.Web.Pages;

public class TextToSpeechModel : PageModel
{
    public List<VoiceOption> Voices { get; set; } = [];
    public string Text { get; set; } = "Hello, Computer! This is Azure AI Speech.";
    public string VoiceName { get; set; } = "en-US-JennyNeural";
    public string? SpeakerProfileId { get; set; }
    public string? AudioBase64 { get; set; }
    public string? Error { get; set; }

    private static readonly List<VoiceOption> DefaultVoices =
    [
        new("en-US-JennyNeural", "Jenny", "Female"),
        new("en-US-GuyNeural", "Guy", "Male"),
        new("en-US-AriaNeural", "Aria", "Female"),
        new("en-US-DavisNeural", "Davis", "Male"),
        new("en-GB-SoniaNeural", "Sonia", "Female"),
        new("en-AU-NatashaNeural", "Natasha", "Female"),
    ];

    public async Task OnGetAsync()
    {
        SpeakerProfileId = SpeechHelper.GetSpeakerProfileId() ?? "";
        await LoadVoicesAsync();
    }

    public async Task<IActionResult> OnPostAsync(string text, string voiceName, string? speakerProfileId)
    {
        Text = text;
        VoiceName = voiceName;
        SpeakerProfileId = speakerProfileId?.Trim();
        await LoadVoicesAsync();

        if (string.IsNullOrWhiteSpace(text))
        {
            Error = "Please enter text to speak.";
            return Page();
        }

        try
        {
            var profileId = string.IsNullOrWhiteSpace(SpeakerProfileId) ? null : SpeakerProfileId;
            var audioBytes = await TextToSpeechService.SynthesizeToBytes(text, voiceName, profileId);
            AudioBase64 = Convert.ToBase64String(audioBytes);
        }
        catch (Exception ex)
        {
            Error = ex.Message;
        }

        return Page();
    }

    private async Task LoadVoicesAsync()
    {
        try
        {
            var voices = await TextToSpeechService.ListVoicesAsync("en-US");
            Voices = voices
                .Select(v => new VoiceOption(v.ShortName, v.LocalName, v.Gender.ToString()))
                .ToList();
        }
        catch
        {
            Voices = DefaultVoices;
        }
    }
}
