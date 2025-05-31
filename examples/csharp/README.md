# Chatterbox TTS API - C# Examples

Examples for using the Chatterbox TTS API with C# and .NET.

## Prerequisites

1. Make sure the API is running: `docker-compose up -d`
2. Install HttpClient and Newtonsoft.Json NuGet packages

## Quick Example

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class TTSRequest
{
    [JsonProperty("text")]
    public string Text { get; set; }
    
    [JsonProperty("exaggeration")]
    public double Exaggeration { get; set; } = 0.7;
    
    [JsonProperty("cfg_weight")]
    public double CfgWeight { get; set; } = 0.6;
    
    [JsonProperty("temperature")]
    public double Temperature { get; set; } = 1.0;
    
    [JsonProperty("return_base64")]
    public bool ReturnBase64 { get; set; } = true;
}

public class TTSResponse
{
    [JsonProperty("success")]
    public bool Success { get; set; }
    
    [JsonProperty("audio_base64")]
    public string AudioBase64 { get; set; }
    
    [JsonProperty("duration_seconds")]
    public double DurationSeconds { get; set; }
    
    [JsonProperty("sample_rate")]
    public int SampleRate { get; set; }
    
    [JsonProperty("message")]
    public string Message { get; set; }
}

public class ChatterboxClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public ChatterboxClient(string baseUrl = "http://localhost:8000")
    {
        _httpClient = new HttpClient();
        _baseUrl = baseUrl;
    }

    public async Task<bool> CheckHealthAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/health");
            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("✅ API is healthy!");
                return true;
            }
            else
            {
                Console.WriteLine($"❌ API health check failed: {response.StatusCode}");
                return false;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Cannot connect to API: {ex.Message}");
            Console.WriteLine("Make sure to run: docker-compose up -d");
            return false;
        }
    }

    public async Task<TTSResponse> GenerateSpeechAsync(TTSRequest request)
    {
        try
        {
            var json = JsonConvert.SerializeObject(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}/tts", content);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (response.IsSuccessStatusCode)
            {
                return JsonConvert.DeserializeObject<TTSResponse>(responseContent);
            }
            else
            {
                return new TTSResponse
                {
                    Success = false,
                    Message = $"HTTP {response.StatusCode}: {responseContent}"
                };
            }
        }
        catch (Exception ex)
        {
            return new TTSResponse
            {
                Success = false,
                Message = ex.Message
            };
        }
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

class Program
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("🎤 Chatterbox TTS API - C# Example");
        Console.WriteLine(new string('=', 50));

        var client = new ChatterboxClient();

        try
        {
            // Check API health
            if (!await client.CheckHealthAsync())
            {
                return;
            }

            // Generate speech
            Console.WriteLine("\n🎵 Generating Speech...");
            var request = new TTSRequest
            {
                Text = "Hello! This is the Chatterbox TTS API working with C# and .NET.",
                Exaggeration = 0.7,
                CfgWeight = 0.6,
                Temperature = 1.0,
                ReturnBase64 = true
            };

            var result = await client.GenerateSpeechAsync(request);

            if (result.Success)
            {
                Console.WriteLine("✅ Speech generated successfully!");
                Console.WriteLine($"   Duration: {result.DurationSeconds:F2}s");
                Console.WriteLine($"   Sample Rate: {result.SampleRate}Hz");
                Console.WriteLine($"   Base64 length: {result.AudioBase64?.Length ?? 0} characters");

                // You could decode base64 and save to file here
                if (!string.IsNullOrEmpty(result.AudioBase64))
                {
                    var audioBytes = Convert.FromBase64String(result.AudioBase64);
                    await File.WriteAllBytesAsync("output.wav", audioBytes);
                    Console.WriteLine("   Audio saved to: output.wav");
                }
            }
            else
            {
                Console.WriteLine($"❌ Generation failed: {result.Message}");
            }
        }
        finally
        {
            client.Dispose();
        }
    }
}
```

## ASP.NET Core Web API Integration

```csharp
[ApiController]
[Route("api/[controller]")]
public class SpeechController : ControllerBase
{
    private readonly ChatterboxClient _ttsClient;

    public SpeechController()
    {
        _ttsClient = new ChatterboxClient();
    }

    [HttpPost("generate")]
    public async Task<IActionResult> GenerateSpeech([FromBody] TTSRequest request)
    {
        if (string.IsNullOrEmpty(request.Text))
        {
            return BadRequest("Text is required");
        }

        var result = await _ttsClient.GenerateSpeechAsync(request);

        if (result.Success)
        {
            if (request.ReturnBase64)
            {
                return Ok(result);
            }
            else
            {
                // Return audio bytes directly
                var audioBytes = Convert.FromBase64String(result.AudioBase64);
                return File(audioBytes, "audio/wav", "speech.wav");
            }
        }
        else
        {
            return StatusCode(500, result.Message);
        }
    }

    [HttpGet("health")]
    public async Task<IActionResult> CheckHealth()
    {
        var isHealthy = await _ttsClient.CheckHealthAsync();
        return Ok(new { healthy = isHealthy });
    }
}
```

## Project File (csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>
```

## Running the Example

```bash
dotnet run
```
