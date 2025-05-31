<?php
/**
 * Chatterbox TTS API - PHP Examples
 * 
 * This file demonstrates how to use the Chatterbox TTS API with PHP.
 * Make sure the API is running: docker-compose up -d
 */

class ChatterboxTTSClient {
    private $baseUrl;
    private $timeout;
    
    public function __construct($baseUrl = 'http://localhost:8000', $timeout = 30) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Check if the API is running and healthy
     */
    public function checkHealth() {
        $response = $this->makeRequest('GET', '/health');
        return $response;
    }
    
    /**
     * Generate speech from text
     */
    public function generateSpeech($text, $options = []) {
        $data = array_merge([
            'text' => $text,
            'exaggeration' => 0.7,
            'cfg_weight' => 0.6,
            'temperature' => 1.0,
            'return_base64' => false
        ], $options);
        
        return $this->makeRequest('POST', '/tts', $data);
    }
    
    /**
     * Generate speech with voice cloning
     */
    public function generateWithVoiceCloning($text, $audioFilePath, $options = []) {
        if (!file_exists($audioFilePath)) {
            throw new Exception("Audio file not found: $audioFilePath");
        }
        
        $data = array_merge([
            'text' => $text,
            'exaggeration' => 0.6,
            'cfg_weight' => 0.7,
            'temperature' => 0.9,
            'return_base64' => false
        ], $options);
        
        return $this->makeFileRequest('/voice-clone', $data, $audioFilePath);
    }
    
    /**
     * Process multiple texts in batch
     */
    public function batchProcess($texts, $options = []) {
        $data = array_merge([
            'texts' => $texts,
            'exaggeration' => 0.6,
            'cfg_weight' => 0.5,
            'temperature' => 1.0
        ], $options);
        
        return $this->makeRequest('POST', '/batch-tts', $data, 120); // Longer timeout for batch
    }
    
    /**
     * Make HTTP request
     */
    private function makeRequest($method, $endpoint, $data = null, $timeout = null) {
        $url = $this->baseUrl . $endpoint;
        $timeout = $timeout ?: $this->timeout;
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $timeout,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        ]);
        
        if ($data && in_array($method, ['POST', 'PUT', 'PATCH'])) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("cURL error: $error");
        }
        
        // Return binary data for audio responses
        if (strpos($contentType, 'audio/') === 0) {
            return [
                'success' => $httpCode === 200,
                'audio_data' => $response,
                'http_code' => $httpCode,
                'content_type' => $contentType
            ];
        }
        
        // Parse JSON response
        $decoded = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Invalid JSON response: " . json_last_error_msg());
        }
        
        return [
            'success' => $httpCode >= 200 && $httpCode < 300,
            'data' => $decoded,
            'http_code' => $httpCode
        ];
    }
    
    /**
     * Make request with file upload
     */
    private function makeFileRequest($endpoint, $data, $audioFilePath) {
        $url = $this->baseUrl . $endpoint;
        
        // Prepare form data
        $postData = $data;
        $postData['audio_file'] = new CURLFile($audioFilePath);
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 60, // Voice cloning takes longer
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postData,
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("cURL error: $error");
        }
        
        // Return binary data for audio responses
        if (strpos($contentType, 'audio/') === 0) {
            return [
                'success' => $httpCode === 200,
                'audio_data' => $response,
                'http_code' => $httpCode,
                'content_type' => $contentType
            ];
        }
        
        // Parse JSON response
        $decoded = json_decode($response, true);
        return [
            'success' => $httpCode >= 200 && $httpCode < 300,
            'data' => $decoded,
            'http_code' => $httpCode
        ];
    }
}

/**
 * Example usage demonstrations
 */
function runExamples() {
    echo "🎤 Chatterbox TTS API - PHP Examples\n";
    echo str_repeat("=", 60) . "\n";
    
    $client = new ChatterboxTTSClient();
    
    try {
        // 1. Health Check
        echo "\n🏥 Checking API Health\n";
        echo str_repeat("-", 50) . "\n";
        
        $health = $client->checkHealth();
        if ($health['success']) {
            $data = $health['data'];
            echo "✅ API is healthy!\n";
            echo "   Device: " . ($data['device'] ?? 'unknown') . "\n";
            echo "   GPU Available: " . ($data['gpu_available'] ? 'Yes' : 'No') . "\n";
            echo "   Sample Rate: " . ($data['sample_rate'] ?? 'unknown') . "\n";
        } else {
            echo "❌ API health check failed\n";
            return;
        }
        
        // 2. Basic TTS
        echo "\n🎵 Basic TTS Example\n";
        echo str_repeat("-", 50) . "\n";
        
        $text = "Hello! This is a demonstration of the Chatterbox TTS API using PHP. The integration is straightforward and powerful.";
        echo "Generating speech for: \"" . substr($text, 0, 50) . "...\"\n";
        
        $result = $client->generateSpeech($text, [
            'exaggeration' => 0.7,
            'cfg_weight' => 0.6,
            'temperature' => 1.0
        ]);
        
        if ($result['success']) {
            $outputFile = 'output_basic.wav';
            file_put_contents($outputFile, $result['audio_data']);
            echo "✅ Audio saved to: $outputFile\n";
            echo "   File size: " . strlen($result['audio_data']) . " bytes\n";
        } else {
            echo "❌ Basic TTS failed\n";
        }
        
        // 3. Base64 TTS
        echo "\n📦 Base64 TTS Example\n";
        echo str_repeat("-", 50) . "\n";
        
        $result = $client->generateSpeech(
            "This audio will be returned as base64 encoded data, perfect for web applications!",
            ['return_base64' => true]
        );
        
        if ($result['success'] && $result['data']['success']) {
            $audioData = base64_decode($result['data']['audio_base64']);
            $outputFile = 'output_base64.wav';
            file_put_contents($outputFile, $audioData);
            
            echo "✅ Audio saved to: $outputFile\n";
            echo "   Duration: " . $result['data']['duration_seconds'] . "s\n";
            echo "   Sample Rate: " . $result['data']['sample_rate'] . "Hz\n";
            echo "   Base64 length: " . strlen($result['data']['audio_base64']) . " characters\n";
        } else {
            echo "❌ Base64 TTS failed\n";
        }
        
        // 4. Voice Cloning (if reference audio exists)
        echo "\n🎭 Voice Cloning Example\n";
        echo str_repeat("-", 50) . "\n";
        
        $referenceAudio = '../test_audio.wav';
        if (file_exists($referenceAudio)) {
            echo "Cloning voice from: $referenceAudio\n";
            
            $result = $client->generateWithVoiceCloning(
                "This is voice cloning in action using PHP! I should sound like the reference audio.",
                $referenceAudio,
                ['exaggeration' => 0.6]
            );
            
            if ($result['success']) {
                $outputFile = 'output_cloned.wav';
                file_put_contents($outputFile, $result['audio_data']);
                echo "✅ Cloned voice saved to: $outputFile\n";
                echo "   File size: " . strlen($result['audio_data']) . " bytes\n";
            } else {
                echo "❌ Voice cloning failed\n";
            }
        } else {
            echo "❌ Reference audio not found: $referenceAudio\n";
            echo "   Please provide a reference audio file to test voice cloning\n";
        }
        
        // 5. Batch Processing
        echo "\n📚 Batch Processing Example\n";
        echo str_repeat("-", 50) . "\n";
        
        $texts = [
            "This is the first sentence in our PHP batch processing demonstration.",
            "Here's the second sentence with different content and style.",
            "And finally, the third sentence completes our batch example.",
            "Bonus fourth sentence showing the power of batch processing!"
        ];
        
        echo "Processing batch of " . count($texts) . " texts...\n";
        
        $result = $client->batchProcess($texts, [
            'exaggeration' => 0.6,
            'cfg_weight' => 0.5
        ]);
        
        if ($result['success'] && $result['data']['success']) {
            echo "✅ Batch processing completed!\n";
            echo "   Total duration: " . $result['data']['total_duration'] . "s\n";
            echo "   Results:\n";
            
            foreach ($result['data']['results'] as $index => $itemResult) {
                if ($itemResult['success']) {
                    $audioData = base64_decode($itemResult['audio_base64']);
                    $outputFile = "output_batch_" . ($index + 1) . ".wav";
                    file_put_contents($outputFile, $audioData);
                    
                    echo "     " . ($index + 1) . ". ✅ $outputFile (" . $itemResult['duration_seconds'] . "s)\n";
                } else {
                    echo "     " . ($index + 1) . ". ❌ Failed: " . ($itemResult['message'] ?? 'Unknown error') . "\n";
                }
            }
        } else {
            echo "❌ Batch processing failed\n";
        }
        
        // 6. Advanced Parameters Demo
        echo "\n🎛️ Advanced Parameters Demo\n";
        echo str_repeat("-", 50) . "\n";
        
        $presets = [
            [
                'name' => 'Subtle & Calm',
                'params' => ['exaggeration' => 0.2, 'cfg_weight' => 0.3, 'temperature' => 0.8],
                'text' => 'This is a calm and subtle voice with minimal emotion.'
            ],
            [
                'name' => 'Expressive & Dynamic',
                'params' => ['exaggeration' => 1.2, 'cfg_weight' => 0.8, 'temperature' => 1.3],
                'text' => 'This voice is very expressive and dynamic with lots of emotion!'
            ],
            [
                'name' => 'Balanced & Natural',
                'params' => ['exaggeration' => 0.5, 'cfg_weight' => 0.5, 'temperature' => 1.0],
                'text' => 'This is a balanced, natural-sounding voice setting.'
            ]
        ];
        
        foreach ($presets as $index => $preset) {
            echo "\nTesting: " . $preset['name'] . "\n";
            echo "Parameters: " . json_encode($preset['params']) . "\n";
            
            $options = array_merge($preset['params'], ['return_base64' => true]);
            $result = $client->generateSpeech($preset['text'], $options);
            
            if ($result['success'] && $result['data']['success']) {
                $audioData = base64_decode($result['data']['audio_base64']);
                $fileName = strtolower(str_replace([' ', '&'], ['_', 'and'], $preset['name']));
                $outputFile = "output_preset_" . ($index + 1) . "_$fileName.wav";
                
                file_put_contents($outputFile, $audioData);
                echo "✅ Saved: $outputFile (" . $result['data']['duration_seconds'] . "s)\n";
            } else {
                echo "❌ Failed: " . ($result['data']['message'] ?? 'Unknown error') . "\n";
            }
        }
        
        echo "\n" . str_repeat("=", 60) . "\n";
        echo "🎉 All examples completed!\n";
        echo "Check the generated audio files in the current directory.\n";
        
    } catch (Exception $e) {
        echo "❌ Error: " . $e->getMessage() . "\n";
    }
}

/**
 * Web Integration Example
 */
function webIntegrationExample() {
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatterbox TTS - PHP Web Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            textarea { width: 100%; height: 100px; margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Chatterbox TTS - PHP Web Demo</h1>
            
            <?php if ($_POST): ?>
                <div class="result">
                    <?php
                    try {
                        $client = new ChatterboxTTSClient();
                        $text = $_POST['text'] ?? '';
                        $exaggeration = floatval($_POST['exaggeration'] ?? 0.7);
                        
                        if (empty($text)) {
                            throw new Exception("Please enter some text.");
                        }
                        
                        $result = $client->generateSpeech($text, [
                            'exaggeration' => $exaggeration,
                            'return_base64' => true
                        ]);
                        
                        if ($result['success'] && $result['data']['success']) {
                            $audioBase64 = $result['data']['audio_base64'];
                            $duration = $result['data']['duration_seconds'];
                            
                            echo "<h3>✅ Speech Generated Successfully!</h3>";
                            echo "<p>Duration: {$duration}s</p>";
                            echo "<audio controls>";
                            echo "<source src='data:audio/wav;base64,$audioBase64' type='audio/wav'>";
                            echo "</audio>";
                        } else {
                            echo "<h3>❌ Generation Failed</h3>";
                            echo "<p>" . ($result['data']['message'] ?? 'Unknown error') . "</p>";
                        }
                    } catch (Exception $e) {
                        echo "<h3>❌ Error</h3>";
                        echo "<p>" . htmlspecialchars($e->getMessage()) . "</p>";
                    }
                    ?>
                </div>
            <?php endif; ?>
            
            <form method="post">
                <label>Text to speak:</label><br>
                <textarea name="text" placeholder="Enter your text here..."><?= htmlspecialchars($_POST['text'] ?? 'Hello! This is a PHP web integration example.') ?></textarea><br>
                
                <label>Exaggeration (0.0 - 2.0):</label><br>
                <input type="range" name="exaggeration" min="0" max="2" step="0.1" value="<?= $_POST['exaggeration'] ?? 0.7 ?>"><br><br>
                
                <button type="submit">🎵 Generate Speech</button>
            </form>
        </div>
    </body>
    </html>
    <?php
}

// Run examples if called directly from command line
if (php_sapi_name() === 'cli') {
    runExamples();
} else {
    // Show web integration example if accessed via web
    webIntegrationExample();
}
?>
