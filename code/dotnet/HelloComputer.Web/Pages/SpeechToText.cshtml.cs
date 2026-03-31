using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using HelloComputer.Web.Services;

namespace HelloComputer.Web.Pages;

public class SpeechToTextModel : PageModel
{
    public string? Transcription { get; set; }
    public string? Error { get; set; }

    public async Task<IActionResult> OnPostAsync(IFormFile? wavFile)
    {
        if (wavFile == null || wavFile.Length == 0)
        {
            Error = "Please select a WAV file.";
            return Page();
        }

        try
        {
            using var ms = new MemoryStream();
            await wavFile.CopyToAsync(ms);
            Transcription = await SpeechToTextService.FromWavBytes(ms.ToArray());
        }
        catch (Exception ex)
        {
            Error = ex.Message;
        }

        return Page();
    }
}
