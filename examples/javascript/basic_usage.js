const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

/**
 * Chatterbox TTS API v3.0 - Node.js Examples
 * 
 * This file demonstrates how to use the enhanced Chatterbox TTS API with Node.js.
 * Features new job tracking, queue system, and multiple output formats.
 * Make sure the API is running: docker-compose up -d
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,  // Increased timeout for queue processing
    responseType: 'json'
});

/**
 * Check if the API is running and healthy
 */
async function checkApiHealth() {
    try {
        console.log('🏥 Checking API health...');
        const response = await api.get('/health');
        
        if (response.status === 200) {
            const health = response.data;
            console.log('✅ API is healthy!');
            console.log(`   Device: ${health.device || 'unknown'}`);
            console.log(`   GPU Available: ${health.gpu_available || false}`);
            console.log(`   Sample Rate: ${health.sample_rate || 'unknown'}`);
            return true;
        } else {
            console.log(`❌ API health check failed: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ Cannot connect to API: ${error.message}`);
        console.log('Make sure to run: docker-compose up -d');
        return false;
    }
}

/**
 * Check current queue status - NEW in v3.0
 */
async function checkQueueStatus() {
    try {
        console.log('📊 Checking queue status...');
        const response = await api.get('/queue/status');
        
        if (response.status === 200) {
            const queue = response.data;
            console.log('📊 Queue Status:');
            console.log(`   Queue Size: ${queue.queue_size || 0}`);
            console.log(`   Active Jobs: ${queue.active_jobs || 0}`);
            console.log(`   Total Processed: ${queue.total_jobs_processed || 0}`);
            return queue;
        } else {
            console.log(`❌ Queue status check failed: ${response.status}`);
            return null;
        }
    } catch (error) {
        console.log(`❌ Cannot get queue status: ${error.message}`);
        return null;
    }
}

/**
 * Check status of a specific job - NEW in v3.0
 */
async function checkJobStatus(jobId) {
    try {
        const response = await api.get(`/job/${jobId}/status`);
        
        if (response.status === 200) {
            return response.data;
        } else {
            console.log(`❌ Job status check failed: ${response.status}`);
            return null;
        }
    } catch (error) {
        console.log(`❌ Cannot get job status: ${error.message}`);
        return null;
    }
}

/**
 * Basic text-to-speech example with job tracking
 */
async function basicTtsExample() {
    console.log('\n🎵 Basic TTS Example (v3.0 Enhanced)');
    console.log('-'.repeat(50));
    
    const ttsRequest = {
        text: "Hello! This is a demonstration of the enhanced Chatterbox TTS API version 3.0 using Node.js. Now with job tracking and multiple output formats!",
        exaggeration: 0.7,
        cfg_weight: 0.6,
        temperature: 1.0,
        output_format: 'wav',  // NEW: wav/mp3/ogg support
        return_base64: false
    };
    
    try {
        console.log(`Generating speech for: "${ttsRequest.text.substring(0, 50)}..."`);
        
        const response = await api.post('/tts', ttsRequest, {
            responseType: 'arraybuffer'  // For binary audio data
        });
        
        if (response.status === 200) {
            // Save the audio file
            const outputFile = 'output_basic.wav';
            fs.writeFileSync(outputFile, Buffer.from(response.data));
            
            // Get metadata from headers
            const duration = response.headers['x-audio-duration'] || 'unknown';
            const sampleRate = response.headers['x-sample-rate'] || 'unknown';
            
            console.log(`✅ Audio saved to: ${outputFile}`);
            console.log(`   Duration: ${duration}s`);
            console.log(`   Sample Rate: ${sampleRate}Hz`);
            console.log(`   File size: ${Buffer.from(response.data).length} bytes`);
        } else {
            console.log(`❌ Request failed: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Request error: ${error.message}`);
        if (error.response) {
            console.log(`   Status: ${error.response.status}`);
            console.log(`   Error: ${error.response.data}`);
        }
    }
}

/**
 * TTS example with base64 encoded response
 */
async function base64TtsExample() {
    console.log('\n📦 Base64 TTS Example');
    console.log('-'.repeat(50));
    
    const ttsRequest = {
        text: "This audio will be returned as base64 encoded data, perfect for web applications and real-time processing!",
        exaggeration: 0.5,
        cfg_weight: 0.5,
        temperature: 1.0,
        return_base64: true
    };
    
    try {
        console.log('Generating speech with base64 output...');
        
        const response = await api.post('/tts', ttsRequest);
        
        if (response.status === 200) {
            const result = response.data;
            
            if (result.success) {
                // Decode and save the audio
                const audioBuffer = Buffer.from(result.audio_base64, 'base64');
                const outputFile = 'output_base64.wav';
                
                fs.writeFileSync(outputFile, audioBuffer);
                
                console.log(`✅ Audio saved to: ${outputFile}`);
                console.log(`   Duration: ${result.duration_seconds.toFixed(2)}s`);
                console.log(`   Sample Rate: ${result.sample_rate}Hz`);
                console.log(`   Base64 length: ${result.audio_base64.length} characters`);
                console.log(`   File size: ${audioBuffer.length} bytes`);
            } else {
                console.log(`❌ Generation failed: ${result.message || 'Unknown error'}`);
            }
        } else {
            console.log(`❌ Request failed: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Request error: ${error.message}`);
    }
}

/**
 * Voice cloning example with reference audio
 */
async function voiceCloningExample() {
    console.log('\n🎭 Voice Cloning Example');
    console.log('-'.repeat(50));
    
    // Check if reference audio exists
    const referenceAudio = '../test_audio.wav';
    if (!fs.existsSync(referenceAudio)) {
        console.log(`❌ Reference audio not found: ${referenceAudio}`);
        console.log('   Please provide a reference audio file to test voice cloning');
        return;
    }
    
    try {
        console.log(`Cloning voice from: ${referenceAudio}`);
        
        // Create form data for file upload
        const formData = new FormData();
        formData.append('text', 'This is voice cloning in action! I should sound like the reference audio you provided.');
        formData.append('exaggeration', '0.6');
        formData.append('cfg_weight', '0.7');
        formData.append('temperature', '0.9');
        formData.append('return_base64', 'false');
        formData.append('audio_file', fs.createReadStream(referenceAudio));
        
        const response = await axios.post(`${API_BASE_URL}/voice-clone`, formData, {
            headers: {
                ...formData.getHeaders(),
            },
            responseType: 'arraybuffer',
            timeout: 60000  // Voice cloning takes longer
        });
        
        if (response.status === 200) {
            const outputFile = 'output_cloned.wav';
            fs.writeFileSync(outputFile, Buffer.from(response.data));
            
            const duration = response.headers['x-audio-duration'] || 'unknown';
            const voiceCloned = response.headers['x-voice-cloned'] || 'false';
            
            console.log(`✅ Cloned voice saved to: ${outputFile}`);
            console.log(`   Duration: ${duration}s`);
            console.log(`   Voice cloned: ${voiceCloned}`);
            console.log(`   File size: ${Buffer.from(response.data).length} bytes`);
        } else {
            console.log(`❌ Voice cloning failed: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Request error: ${error.message}`);
        if (error.response) {
            console.log(`   Status: ${error.response.status}`);
        }
    }
}

/**
 * Batch processing multiple texts
 */
async function batchProcessingExample() {
    console.log('\n📚 Batch Processing Example');
    console.log('-'.repeat(50));
    
    const batchRequest = {
        texts: [
            "This is the first sentence in our batch processing demonstration.",
            "Here's the second sentence with different content and style.",
            "And finally, the third sentence completes our batch example.",
            "Bonus fourth sentence showing the power of batch processing!"
        ],
        exaggeration: 0.6,
        cfg_weight: 0.5,
        temperature: 1.0
    };
    
    try {
        console.log(`Processing batch of ${batchRequest.texts.length} texts...`);
        
        const response = await api.post('/batch-tts', batchRequest, {
            timeout: 120000  // Batch processing takes longer
        });
        
        if (response.status === 200) {
            const result = response.data;
            
            if (result.success) {
                console.log(`✅ Batch processing completed!`);
                console.log(`   Total duration: ${result.total_duration.toFixed(2)}s`);
                console.log('   Results:');
                
                result.results.forEach((itemResult, index) => {
                    if (itemResult.success) {
                        // Decode and save each audio file
                        const audioBuffer = Buffer.from(itemResult.audio_base64, 'base64');
                        const outputFile = `output_batch_${index + 1}.wav`;
                        
                        fs.writeFileSync(outputFile, audioBuffer);
                        
                        console.log(`     ${index + 1}. ✅ ${outputFile} (${itemResult.duration_seconds.toFixed(2)}s)`);
                    } else {
                        console.log(`     ${index + 1}. ❌ Failed: ${itemResult.message || 'Unknown error'}`);
                    }
                });
            } else {
                console.log('❌ Batch processing failed');
            }
        } else {
            console.log(`❌ Batch request failed: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Request error: ${error.message}`);
    }
}

/**
 * Demonstrate different parameter combinations
 */
async function advancedParametersDemo() {
    console.log('\n🎛️ Advanced Parameters Demo');
    console.log('-'.repeat(50));
    
    const parameterSets = [
        {
            name: "Subtle & Calm",
            params: { exaggeration: 0.2, cfg_weight: 0.3, temperature: 0.8 },
            text: "This is a calm and subtle voice with minimal emotion."
        },
        {
            name: "Expressive & Dynamic",
            params: { exaggeration: 1.2, cfg_weight: 0.8, temperature: 1.3 },
            text: "This voice is very expressive and dynamic with lots of emotion!"
        },
        {
            name: "Balanced & Natural",
            params: { exaggeration: 0.5, cfg_weight: 0.5, temperature: 1.0 },
            text: "This is a balanced, natural-sounding voice setting."
        }
    ];
    
    for (let i = 0; i < parameterSets.length; i++) {
        const preset = parameterSets[i];
        console.log(`\nTesting: ${preset.name}`);
        console.log(`Parameters: ${JSON.stringify(preset.params)}`);
        
        const requestData = {
            text: preset.text,
            return_base64: true,
            ...preset.params
        };
        
        try {
            const response = await api.post('/tts', requestData);
            
            if (response.status === 200) {
                const result = response.data;
                if (result.success) {
                    // Save the audio
                    const audioBuffer = Buffer.from(result.audio_base64, 'base64');
                    const outputFile = `output_preset_${i + 1}_${preset.name.toLowerCase().replace(/\s+/g, '_')}.wav`;
                    
                    fs.writeFileSync(outputFile, audioBuffer);
                    
                    console.log(`✅ Saved: ${outputFile} (${result.duration_seconds.toFixed(2)}s)`);
                } else {
                    console.log(`❌ Failed: ${result.message || 'Unknown error'}`);
                }
            } else {
                console.log(`❌ Request failed: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ Request error: ${error.message}`);
        }
    }
}

/**
 * Main function to run all examples
 */
async function main() {
    console.log('🎤 Chatterbox TTS API - Node.js Examples');
    console.log('='.repeat(60));
    
    // Check API health first
    const isHealthy = await checkApiHealth();
    if (!isHealthy) {
        return;
    }
    
    // Run examples
    await basicTtsExample();
    await base64TtsExample();
    await voiceCloningExample();
    await batchProcessingExample();
    await advancedParametersDemo();
    
    console.log('\n' + '='.repeat(60));
    console.log('🎉 All examples completed!');
    console.log('Check the generated audio files in the current directory.');
}

// Run if this script is executed directly
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Unexpected error:', error.message);
        process.exit(1);
    });
}

// Export functions for use in other modules
module.exports = {
    checkApiHealth,
    basicTtsExample,
    base64TtsExample,
    voiceCloningExample,
    batchProcessingExample,
    advancedParametersDemo
};
