using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using HelloComputer.Web.Services;

namespace HelloComputer.Web.Pages;

public class ChatModel : PageModel
{
    public List<VoiceOption> Voices { get; set; } = [];
    public string VoiceName { get; set; } = "en-US-JennyNeural";
    public string SystemPrompt { get; set; } =
        "You are a helpful assistant. Keep your responses concise -- no more than two or three sentences.";
    public string UserMessage { get; set; } = "";
    public string? AiResponse { get; set; }
    public string? AudioBase64 { get; set; }
    public string? Error { get; set; }

    private static readonly List<VoiceOption> DefaultVoices =
    [
        new("en-US-JennyNeural", "Jenny", "Female"),
        new("en-US-GuyNeural", "Guy", "Male"),
        new("en-US-AriaNeural", "Aria", "Female"),
        new("en-US-DavisNeural", "Davis", "Male"),
    ];

    public async Task OnGetAsync()
    {
        await LoadVoicesAsync();
    }

    public async Task<IActionResult> OnPostAsync(
        string userMessage, string voiceName, string systemPrompt)
    {
        UserMessage = userMessage;
        VoiceName = voiceName;
        SystemPrompt = systemPrompt;
        await LoadVoicesAsync();

        if (string.IsNullOrWhiteSpace(userMessage))
        {
            Error = "Please enter a message.";
            return Page();
        }

        try
        {
            AiResponse = await ChatService.SendAsync(userMessage, systemPrompt);

            var audioBytes = await TextToSpeechService.SynthesizeToBytes(AiResponse, voiceName);
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
