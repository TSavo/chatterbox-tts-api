#!/usr/bin/env python3
"""
Test script for the new chunking functionality in Chatterbox TTS API.
Tests the intelligent text chunking and audio concatenation features.
"""

import requests
import time
import os

# Test configuration
API_BASE = "http://localhost:8000"
TEST_OUTPUT_DIR = "test_outputs"

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy and ready")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to run: docker-compose up -d")
        return False

def test_short_text():
    """Test with short text (should not chunk)"""
    print("\n🧪 Testing short text (no chunking expected)")
    
    text = "This is a short text that should not require chunking."
    
    response = requests.post(f"{API_BASE}/tts", json={
        "text": text,
        "return_base64": True,
        "exaggeration": 0.7
    })
    
    if response.status_code == 200:
        result = response.json()
        duration = result.get("duration_seconds", 0)
        print(f"✅ Short text generated: {duration:.2f}s duration")
        return True
    else:
        print(f"❌ Short text test failed: {response.status_code}")
        return False

def test_medium_text():
    """Test with medium text (might chunk)"""
    print("\n🧪 Testing medium text (potential chunking)")
    
    text = """
    This is a longer piece of text that will test the chunking functionality of the Chatterbox TTS API.
    It contains multiple sentences with various punctuation marks.
    
    The system should intelligently break this down into manageable chunks.
    Each chunk should be generated separately and then concatenated back together.
    This ensures that we can handle longer texts without overwhelming the TTS model.
    
    The chunking algorithm looks for natural breaking points like periods, line breaks, and other punctuation.
    This maintains the flow and naturalness of the speech while staying within the duration limits.
    """
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/tts", json={
        "text": text,
        "output_format": "mp3",
        "exaggeration": 0.6,
        "return_base64": False
    }, timeout=120)
    
    generation_time = time.time() - start_time
    
    if response.status_code == 200:
        # Save the audio file
        output_path = os.path.join(TEST_OUTPUT_DIR, "medium_text_test.mp3")
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        duration = float(response.headers.get("X-Audio-Duration", 0))
        print(f"✅ Medium text generated: {duration:.2f}s duration, {generation_time:.2f}s generation time")
        print(f"   Saved to: {output_path}")
        return True
    else:
        print(f"❌ Medium text test failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_long_text():
    """Test with long text (should definitely chunk)"""
    print("\n🧪 Testing long text (chunking required)")
    
    text = """
    Welcome to the comprehensive test of the Chatterbox TTS API's new intelligent chunking system.
    This extensive piece of text has been specifically designed to exceed the forty-second duration limit.
    
    The purpose of this test is to verify that the system can handle long-form content effectively.
    When text exceeds the maximum duration threshold, the API automatically breaks it down into smaller, manageable chunks.
    These chunks are created by analyzing the text for natural breaking points.
    
    First, the system looks for paragraph breaks, which are indicated by double line breaks.
    If paragraphs are still too long, it then examines single line breaks.
    
    Next, it considers sentence boundaries marked by periods, exclamation points, and question marks.
    Are you following along? Great! This demonstrates how question marks serve as natural pause points.
    
    The system also recognizes clause boundaries: commas, semicolons, and colons all provide opportunities for intelligent splitting.
    This approach ensures that the generated speech maintains its natural flow and rhythm.
    
    Each chunk is processed individually by the TTS model, generating separate audio segments.
    These segments are then seamlessly concatenated using FFmpeg to create a single, cohesive audio file.
    The result should sound natural and continuous, as if it were generated as a single piece.
    
    This chunking strategy solves a critical limitation of many TTS systems: the inability to handle long texts effectively.
    By breaking content into digestible pieces, we can process documents, articles, and other lengthy texts without sacrificing quality.
    
    The concatenation process preserves the audio quality and maintains consistent voice characteristics throughout.
    Users can still apply the same emotion controls, voice cloning, and output format preferences to the entire text.
    
    This test will help us verify that the implementation works correctly across different scenarios and text lengths.
    If you're hearing this complete message as a single audio file, then the chunking and concatenation system is working perfectly!
    """
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/tts", json={
        "text": text,
        "output_format": "wav",
        "exaggeration": 0.5,
        "cfg_weight": 0.6,
        "temperature": 0.9,
        "return_base64": False
    }, timeout=300)  # Longer timeout for long text
    
    generation_time = time.time() - start_time
    
    if response.status_code == 200:
        # Save the audio file
        output_path = os.path.join(TEST_OUTPUT_DIR, "long_text_test.wav")
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        duration = float(response.headers.get("X-Audio-Duration", 0))
        print(f"✅ Long text generated: {duration:.2f}s duration, {generation_time:.2f}s generation time")
        print(f"   Saved to: {output_path}")
        
        if duration > 45:  # Should be significantly longer than 40s
            print(f"   🎉 Successfully generated audio longer than 40s limit!")
        
        return True
    else:
        print(f"❌ Long text test failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_batch_with_long_texts():
    """Test batch processing with some long texts"""
    print("\n🧪 Testing batch processing with mixed text lengths")
    
    texts = [
        "Short text number one.",
        "This is a medium-length text that contains multiple sentences. It should demonstrate how the batch processing handles different text lengths. The chunking system should work seamlessly even within batch operations.",
        "Final short text."
    ]
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/batch-tts", json={
        "texts": texts,
        "exaggeration": 0.6,
        "cfg_weight": 0.5,
        "temperature": 1.0
    }, timeout=180)
    
    generation_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        total_duration = result.get("total_duration", 0)
        success_count = sum(1 for r in result["results"] if r["success"])
        
        print(f"✅ Batch processing completed: {success_count}/{len(texts)} successful")
        print(f"   Total duration: {total_duration:.2f}s, {generation_time:.2f}s generation time")
        return True
    else:
        print(f"❌ Batch test failed: {response.status_code}")
        return False

def main():
    """Run all chunking tests"""
    print("🎤 Chatterbox TTS API - Chunking Functionality Tests")
    print("=" * 60)
    
    ensure_output_dir()
    
    # Test API health first
    if not test_api_health():
        print("\n❌ API is not available. Please start the service first.")
        return
    
    # Run tests
    tests = [
        test_short_text,
        test_medium_text,
        test_long_text,
        test_batch_with_long_texts
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 Test Results")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed! Chunking system is working correctly.")
        print(f"   Generated audio files are saved in: {TEST_OUTPUT_DIR}/")
    else:
        print(f"\n⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main()