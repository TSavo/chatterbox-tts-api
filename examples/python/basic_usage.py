#!/usr/bin/env python3
"""
Chatterbox TTS API v3.0 - Python Examples

This file demonstrates how to use the enhanced Chatterbox TTS API with Python.
Features new job tracking, queue system, and multiple output formats.
Make sure the API is running: docker-compose up -d
"""

import requests
import base64
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy!")
            print(f"   Device: {health_data.get('device', 'unknown')}")
            print(f"   GPU Available: {health_data.get('gpu_available', False)}")
            print(f"   Sample Rate: {health_data.get('sample_rate', 'unknown')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to run: docker-compose up -d")
        return False

def check_queue_status():
    """Check current queue status - NEW in v3.0"""
    try:
        response = requests.get(f"{API_BASE_URL}/queue/status", timeout=5)
        if response.status_code == 200:
            queue_data = response.json()
            print(f"📊 Queue Status:")
            print(f"   Queue Size: {queue_data.get('queue_size', 0)}")
            print(f"   Active Jobs: {queue_data.get('active_jobs', 0)}")
            print(f"   Total Processed: {queue_data.get('total_jobs_processed', 0)}")
            return queue_data
        else:
            print(f"❌ Queue status check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot get queue status: {e}")
        return None

def check_job_status(job_id: str):
    """Check status of a specific job - NEW in v3.0"""
    try:
        response = requests.get(f"{API_BASE_URL}/job/{job_id}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Job status check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot get job status: {e}")
        return None

def basic_tts_example():
    """Basic text-to-speech example with job tracking"""
    print("\n🎵 Basic TTS Example (v3.0 Enhanced)")
    print("-" * 50)
    
    # Request payload with new output_format parameter
    tts_request = {
        "text": "Hello! This is a demonstration of the enhanced Chatterbox TTS API version 3.0. Now with job tracking and multiple output formats!",
        "exaggeration": 0.7,  # Higher emotion
        "cfg_weight": 0.6,    # Good guidance
        "temperature": 1.0,   # Normal randomness
        "output_format": "wav",  # NEW: wav/mp3/ogg support
        "return_base64": False  # Return binary audio
    }
      try:
        print(f"Generating speech for: '{tts_request['text'][:50]}...'")
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=tts_request,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save the audio file
            output_file = Path("output_basic.wav")
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            # Get metadata from headers (NEW in v3.0)
            job_id = response.headers.get('X-Job-ID', 'unknown')
            duration = response.headers.get('X-Audio-Duration', 'unknown')
            sample_rate = response.headers.get('X-Sample-Rate', 'unknown')
            output_format = response.headers.get('X-Output-Format', 'wav')
            
            print(f"✅ Audio generated successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   Output file: {output_file}")
            print(f"   Duration: {duration}s")
            print(f"   Sample rate: {sample_rate}Hz")
            print(f"   Format: {output_format}")
            print(f"   File size: {output_file.stat().st_size} bytes")
            
            return job_id
        else:
            print(f"❌ TTS request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def output_format_example():
    """Demonstrate different output formats - NEW in v3.0"""
    print("\n🎵 Output Format Examples (v3.0)")
    print("-" * 50)
    
    formats = ["wav", "mp3", "ogg"]
    text = "Testing different audio formats: WAV, MP3, and OGG. Each has different compression and quality characteristics."
    
    for format_type in formats:
        print(f"\nGenerating {format_type.upper()} format...")
        
        tts_request = {
            "text": text,
            "exaggeration": 0.6,
            "cfg_weight": 0.5,
            "temperature": 1.0,
            "output_format": format_type,
            "return_base64": False
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/tts",
                json=tts_request,
                timeout=30
            )
            
            if response.status_code == 200:
                output_file = Path(f"output_format_test.{format_type}")
                with open(output_file, "wb") as f:
                    f.write(response.content)
                
                job_id = response.headers.get('X-Job-ID', 'unknown')
                duration = response.headers.get('X-Audio-Duration', 'unknown')
                actual_format = response.headers.get('X-Output-Format', format_type)
                
                print(f"✅ {format_type.upper()} generated successfully!")
                print(f"   Job ID: {job_id}")
                print(f"   File: {output_file}")
                print(f"   Size: {output_file.stat().st_size} bytes")
                print(f"   Duration: {duration}s")
                print(f"   Actual format: {actual_format}")
            else:
                print(f"❌ {format_type.upper()} generation failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {format_type.upper()} request failed: {e}")

def base64_tts_example():
    """Base64 TTS example with job tracking"""
    print("\n📦 Base64 TTS Example (v3.0 Enhanced)")
    print("-" * 50)
    
    tts_request = {
        "text": "This audio will be returned as base64 encoded data, perfect for web applications and real-time processing!",
        "exaggeration": 0.8,
        "cfg_weight": 0.7,
        "temperature": 1.1,
        "output_format": "mp3",  # NEW: Can specify format for base64 too
        "return_base64": True
    }
    
    try:
        print(f"Generating base64 audio...")
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=tts_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                # Decode base64 audio
                audio_data = base64.b64decode(result["audio_base64"])
                output_file = Path("output_base64.mp3")
                
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                
                print(f"✅ Base64 audio generated successfully!")
                print(f"   Job ID: {result.get('job_id', 'unknown')}")
                print(f"   Output file: {output_file}")
                print(f"   Duration: {result.get('duration_seconds', 'unknown')}s")
                print(f"   Sample rate: {result.get('sample_rate', 'unknown')}Hz")
                print(f"   Base64 length: {len(result['audio_base64'])} characters")
                print(f"   Decoded size: {len(audio_data)} bytes")
                
                return result.get('job_id')
            else:
                print(f"❌ Base64 TTS failed: {result.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Base64 TTS request failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Base64 request failed: {e}")
        return None
            sample_rate = response.headers.get('X-Sample-Rate', 'unknown')
            
            print(f"✅ Audio saved to: {output_file}")
            print(f"   Duration: {duration}s")
            print(f"   Sample Rate: {sample_rate}Hz")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def base64_tts_example():
    """TTS example with base64 encoded response"""
    print("\n📦 Base64 TTS Example")
    print("-" * 50)
    
    tts_request = {
        "text": "This audio will be returned as base64 encoded data, perfect for web applications!",
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "temperature": 1.0,
        "return_base64": True  # Return JSON with base64 audio
    }
    
    try:
        print(f"Generating speech with base64 output...")
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=tts_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                # Decode and save the audio
                audio_data = base64.b64decode(result["audio_base64"])
                output_file = Path("output_base64.wav")
                
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                
                print(f"✅ Audio saved to: {output_file}")
                print(f"   Duration: {result['duration_seconds']:.2f}s")
                print(f"   Sample Rate: {result['sample_rate']}Hz")
                print(f"   Base64 length: {len(result['audio_base64'])} characters")
            else:
                print(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def voice_cloning_example():
    """Voice cloning example with reference audio"""
    print("\n🎭 Voice Cloning Example")
    print("-" * 50)
    
    # Check if reference audio exists
    reference_audio = Path("../test_audio.wav")  # Assuming test audio exists
    if not reference_audio.exists():
        print(f"❌ Reference audio not found: {reference_audio}")
        print("   Please provide a reference audio file to test voice cloning")
        return
    
    clone_request = {
        "text": "This is voice cloning in action! I should sound like the reference audio you provided.",
        "exaggeration": 0.6,
        "cfg_weight": 0.7,
        "temperature": 0.9,
        "return_base64": False
    }
    
    try:
        print(f"Cloning voice from: {reference_audio}")
        print(f"Text to generate: '{clone_request['text'][:50]}...'")
        
        with open(reference_audio, "rb") as audio_file:
            response = requests.post(
                f"{API_BASE_URL}/voice-clone",
                data=clone_request,
                files={"audio_file": audio_file},
                timeout=60  # Voice cloning takes longer
            )
        
        if response.status_code == 200:
            output_file = Path("output_cloned.wav")
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            duration = response.headers.get('X-Audio-Duration', 'unknown')
            print(f"✅ Cloned voice saved to: {output_file}")
            print(f"   Duration: {duration}s")
            print(f"   Voice cloned: {response.headers.get('X-Voice-Cloned', 'false')}")
            
        else:
            print(f"❌ Voice cloning failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def batch_processing_example():
    """Batch processing multiple texts"""
    print("\n📚 Batch Processing Example")
    print("-" * 50)
    
    batch_request = {
        "texts": [
            "This is the first sentence in our batch.",
            "Here's the second sentence with different content.",
            "And finally, the third sentence completes our batch.",
            "Bonus fourth sentence for good measure!"
        ],
        "exaggeration": 0.6,
        "cfg_weight": 0.5,
        "temperature": 1.0
    }
    
    try:
        print(f"Processing batch of {len(batch_request['texts'])} texts...")
        
        response = requests.post(
            f"{API_BASE_URL}/batch-tts",
            json=batch_request,
            timeout=120  # Batch processing takes longer
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                print(f"✅ Batch processing completed!")
                print(f"   Total duration: {result['total_duration']:.2f}s")
                print(f"   Results:")
                
                for i, item_result in enumerate(result["results"]):
                    if item_result["success"]:
                        # Decode and save each audio file
                        audio_data = base64.b64decode(item_result["audio_base64"])
                        output_file = Path(f"output_batch_{i+1}.wav")
                        
                        with open(output_file, "wb") as f:
                            f.write(audio_data)
                        
                        print(f"     {i+1}. ✅ {output_file} ({item_result['duration_seconds']:.2f}s)")
                    else:
                        print(f"     {i+1}. ❌ Failed: {item_result.get('message', 'Unknown error')}")
            else:
                print(f"❌ Batch processing failed")
                
        else:
            print(f"❌ Batch request failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def advanced_parameters_demo():
    """Demonstrate different parameter combinations"""
    print("\n🎛️ Advanced Parameters Demo")
    print("-" * 50)
    
    # Different parameter combinations to showcase
    parameter_sets = [
        {
            "name": "Subtle & Calm",
            "params": {"exaggeration": 0.2, "cfg_weight": 0.3, "temperature": 0.8},
            "text": "This is a calm and subtle voice with minimal emotion."
        },
        {
            "name": "Expressive & Dynamic",
            "params": {"exaggeration": 1.2, "cfg_weight": 0.8, "temperature": 1.3},
            "text": "This voice is very expressive and dynamic with lots of emotion!"
        },
        {
            "name": "Balanced & Natural",
            "params": {"exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 1.0},
            "text": "This is a balanced, natural-sounding voice setting."
        }
    ]
    
    for i, preset in enumerate(parameter_sets):
        print(f"\nTesting: {preset['name']}")
        print(f"Parameters: {preset['params']}")
        
        request_data = {
            "text": preset["text"],
            "return_base64": True,
            **preset["params"]
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/tts",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    # Save the audio
                    audio_data = base64.b64decode(result["audio_base64"])
                    output_file = Path(f"output_preset_{i+1}_{preset['name'].lower().replace(' ', '_')}.wav")
                    
                    with open(output_file, "wb") as f:
                        f.write(audio_data)
                    
                    print(f"✅ Saved: {output_file} ({result['duration_seconds']:.2f}s)")
                else:
                    print(f"❌ Failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")

def main():
    """Run all examples"""
    print("🎤 Chatterbox TTS API - Python Examples")
    print("=" * 60)
    
    # Check API health first
    if not check_api_health():
        return
    
    # Run examples
    basic_tts_example()
    base64_tts_example()
    voice_cloning_example()
    batch_processing_example()
    advanced_parameters_demo()
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("Check the generated audio files in the current directory.")

if __name__ == "__main__":
    main()
