using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace HelloComputer.Web.Services;

public record PronunciationSample(string Title, string Language, string Text);

public static class PronunciationSamples
{
    private static List<PronunciationSample>? _cached;

    public static List<PronunciationSample> Load()
    {
        if (_cached != null) return _cached;

        var path = FindSamplesFile();
        if (path == null)
        {
            _cached = [];
            return _cached;
        }

        var yaml = File.ReadAllText(path);
        var deserializer = new DeserializerBuilder()
            .WithNamingConvention(CamelCaseNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .Build();

        var root = deserializer.Deserialize<SamplesRoot>(yaml);
        _cached = root?.Samples ?? [];
        return _cached;
    }

    private static string? FindSamplesFile()
    {
        // Walk up from the content root to find code/samples/pronunciation_inputs.yaml.
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        for (int i = 0; i < 8 && dir != null; i++, dir = dir.Parent)
        {
            var candidate = Path.Combine(dir.FullName, "code", "samples", "pronunciation_inputs.yaml");
            if (File.Exists(candidate)) return candidate;
        }
        return null;
    }

    private class SamplesRoot
    {
        public List<PronunciationSample> Samples { get; set; } = [];
    }
}
