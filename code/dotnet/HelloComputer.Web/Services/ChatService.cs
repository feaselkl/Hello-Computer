using Azure.AI.OpenAI;
using OpenAI.Chat;

namespace HelloComputer.Web.Services;

public static class ChatService
{
    public static async Task<string> SendAsync(string userMessage, string systemMessage = "You are a helpful assistant.")
    {
        var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");
        var apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY");
        var deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT");

        if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(deployment))
        {
            throw new InvalidOperationException(
                "Missing environment variables. " +
                "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and " +
                "AZURE_OPENAI_DEPLOYMENT (or update your .env file).");
        }

        var client = new AzureOpenAIClient(
            new Uri(endpoint),
            new System.ClientModel.ApiKeyCredential(apiKey));

        var chatClient = client.GetChatClient(deployment);

        var completion = await chatClient.CompleteChatAsync(
        [
            new SystemChatMessage(systemMessage),
            new UserChatMessage(userMessage),
        ]);

        return completion.Value.Content[0].Text;
    }
}
