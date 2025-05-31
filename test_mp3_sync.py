#!/usr/bin/env python3
"""
Test script for synchronous MP3 generation from Chatterbox TTS API
"""

import requests
import time

def test_sync_mp3():
    """Test synchronous MP3 generation"""
    
    # API endpoint
    url = "http://localhost:8000/tts"
    
    # Test data for MP3 generation
    test_data = {
        "text": "Hello! This is a test of the Chatterbox TTS API generating MP3 audio synchronously.",
        "exaggeration": 0.7,
        "cfg_weight": 0.4,
        "temperature": 1.1,
        "output_format": "mp3",
        "return_base64": False  # We want binary MP3 data
    }
    
    print("🎵 Testing Synchronous MP3 Generation...")
    print(f"📝 Text: {test_data['text']}")
    print(f"🎛️  Parameters: exaggeration={test_data['exaggeration']}, cfg_weight={test_data['cfg_weight']}")
    print(f"🔊 Format: {test_data['output_format']}")
    print()
    
    # Record start time
    start_time = time.time()
    
    try:
        # Make synchronous request
        print("⏳ Sending request to TTS API...")
        response = requests.post(url, json=test_data, timeout=300)
        
        # Check if request was successful
        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            
            # Get response headers
            headers = response.headers
            audio_duration = headers.get('X-Audio-Duration', 'Unknown')
            sample_rate = headers.get('X-Sample-Rate', 'Unknown')
            job_id = headers.get('X-Job-ID', 'Unknown')
            output_format = headers.get('X-Output-Format', 'Unknown')
            content_type = headers.get('Content-Type', 'Unknown')
            
            print("✅ Success!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print(f"🎵 Audio duration: {audio_duration} seconds")
            print(f"📊 Sample rate: {sample_rate} Hz")
            print(f"🆔 Job ID: {job_id}")
            print(f"📁 Output format: {output_format}")
            print(f"📋 Content type: {content_type}")
            print(f"📦 File size: {len(response.content)} bytes")
            
            # Save the MP3 file
            filename = f"test_output_{int(time.time())}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"💾 Saved MP3 file: {filename}")
            print()
            print("🎉 Synchronous MP3 generation completed successfully!")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the API running on localhost:8000?")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

def test_sync_wav():
    """Test synchronous WAV generation for comparison"""
    
    url = "http://localhost:8000/tts"
    
    test_data = {
        "text": "This is the same text but in WAV format for comparison.",
        "exaggeration": 0.7,
        "cfg_weight": 0.4,
        "temperature": 1.1,
        "output_format": "wav",
        "return_base64": False
    }
    
    print("🎵 Testing Synchronous WAV Generation...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=test_data, timeout=300)
        
        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            
            headers = response.headers
            content_type = headers.get('Content-Type', 'Unknown')
            
            print("✅ WAV Success!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print(f"📋 Content type: {content_type}")
            print(f"📦 File size: {len(response.content)} bytes")
            
            # Save the WAV file
            filename = f"test_output_{int(time.time())}.wav"
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"💾 Saved WAV file: {filename}")
            
    except Exception as e:
        print(f"💥 WAV test error: {e}")

def test_queue_status():
    """Check queue status"""
    try:
        response = requests.get("http://localhost:8000/queue/status")
        if response.status_code == 200:
            status = response.json()
            print("📊 Queue Status:")
            print(f"   Queue size: {status['queue_size']}")
            print(f"   Active jobs: {status['active_jobs']}")
            print(f"   Total processed: {status['total_jobs_processed']}")
        else:
            print(f"❌ Queue status error: {response.status_code}")
    except Exception as e:
        print(f"💥 Queue status error: {e}")

if __name__ == "__main__":
    print("🚀 Chatterbox TTS API - Synchronous MP3 Test")
    print("=" * 50)
    
    # Check queue status first
    test_queue_status()
    print()
    
    # Test MP3 generation
    test_sync_mp3()
    print()
    
    # Test WAV for comparison
    test_sync_wav()
    print()
    
    # Check queue status after
    test_queue_status()
    
    print("\n🎯 Test completed! Check the generated audio files.")
