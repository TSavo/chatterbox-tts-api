# Chatterbox TTS API - Go Examples

Simple Go examples for using the Chatterbox TTS API.

## Prerequisites

1. Make sure the API is running: `docker-compose up -d`
2. Install Go dependencies: `go mod init chatterbox-examples && go mod tidy`

## Quick Example

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "os"
)

type TTSRequest struct {
    Text         string  `json:"text"`
    Exaggeration float64 `json:"exaggeration"`
    CFGWeight    float64 `json:"cfg_weight"`
    Temperature  float64 `json:"temperature"`
    ReturnBase64 bool    `json:"return_base64"`
}

type TTSResponse struct {
    Success         bool    `json:"success"`
    AudioBase64     string  `json:"audio_base64,omitempty"`
    DurationSeconds float64 `json:"duration_seconds"`
    SampleRate      int     `json:"sample_rate"`
    Message         string  `json:"message,omitempty"`
}

func main() {
    // Basic TTS example
    request := TTSRequest{
        Text:         "Hello! This is the Chatterbox TTS API working with Go.",
        Exaggeration: 0.7,
        CFGWeight:    0.6,
        Temperature:  1.0,
        ReturnBase64: true,
    }

    response, err := generateSpeech(request)
    if err != nil {
        fmt.Printf("❌ Error: %v\n", err)
        return
    }

    if response.Success {
        fmt.Printf("✅ Generated %.2fs of audio\n", response.DurationSeconds)
        fmt.Printf("   Sample Rate: %dHz\n", response.SampleRate)
        
        // You could decode base64 and save to file here
        fmt.Printf("   Base64 length: %d characters\n", len(response.AudioBase64))
    } else {
        fmt.Printf("❌ Generation failed: %s\n", response.Message)
    }
}

func generateSpeech(request TTSRequest) (*TTSResponse, error) {
    jsonData, err := json.Marshal(request)
    if err != nil {
        return nil, err
    }

    resp, err := http.Post(
        "http://localhost:8000/tts",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var response TTSResponse
    err = json.Unmarshal(body, &response)
    if err != nil {
        return nil, err
    }

    return &response, nil
}
```

## Running the Example

```bash
go run basic_usage.go
```

## Health Check Example

```go
func checkHealth() error {
    resp, err := http.Get("http://localhost:8000/health")
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode == 200 {
        fmt.Println("✅ API is healthy!")
        return nil
    } else {
        return fmt.Errorf("API health check failed: %d", resp.StatusCode)
    }
}
```
