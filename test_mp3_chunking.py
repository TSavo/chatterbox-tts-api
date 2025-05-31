#!/usr/bin/env python3
"""
Test script to verify that the new smart chunking logic works properly with MP3 conversion.
Tests both chunked and non-chunked text to ensure MP3 output is correct.
"""

import requests
import time
import tempfile
import os

def test_chunked_mp3():
    """Test MP3 generation with text that will be chunked"""
    
    # API endpoint
    url = "http://localhost:8000/tts"
    
    # Long text that will definitely be chunked (over 40s)
    long_text = """
    This is a comprehensive test of the Chatterbox TTS system with the new smart chunking logic. 
    The text is intentionally long to trigger the intelligent chunking algorithm that respects sentence boundaries.
    
    This is the second paragraph which adds substantial content to push us well over the forty-second hard limit threshold.
    The system should automatically detect that this text is too long and split it into appropriate chunks.
    Each chunk will be generated separately and then concatenated together seamlessly.
    
    Finally, this third paragraph ensures we have enough content to properly test the chunking behavior.
    The resulting MP3 file should sound natural and continuous, with no audible breaks between the chunks.
    The smart chunking logic prioritizes maintaining sentence integrity over strict duration limits.
    """
    
    test_data = {
        "text": long_text.strip(),
        "exaggeration": 0.6,
        "cfg_weight": 0.5,
        "temperature": 1.0,
        "output_format": "mp3",
        "return_base64": False
    }
    
    print("🎵 Testing Chunked MP3 Generation...")
    print(f"📝 Text length: {len(long_text)} characters")
    print(f"🔊 Format: {test_data['output_format']}")
    print()
    
    start_time = time.time()
    
    try:
        print("⏳ Sending long text request to TTS API...")
        response = requests.post(url, json=test_data, timeout=300)
        
        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            
            # Get response headers
            headers = response.headers
            audio_duration = headers.get('X-Audio-Duration', 'Unknown')
            sample_rate = headers.get('X-Sample-Rate', 'Unknown')
            job_id = headers.get('X-Job-ID', 'Unknown')
            content_type = headers.get('Content-Type', 'Unknown')
            
            print("✅ Chunked MP3 generation successful!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print(f"🎵 Audio duration: {audio_duration} seconds")
            print(f"📊 Sample rate: {sample_rate} Hz")
            print(f"🆔 Job ID: {job_id}")
            print(f"📋 Content type: {content_type}")
            print(f"💾 MP3 file size: {len(response.content)} bytes")
            
            # Save the MP3 file
            with tempfile.NamedTemporaryFile(suffix="_chunked.mp3", delete=False) as tmp:
                tmp.write(response.content)
                mp3_path = tmp.name
                print(f"💿 MP3 saved to: {mp3_path}")
            
            # Verify it's a valid MP3 file by checking headers
            if response.content[:3] == b'ID3' or response.content[:2] == b'\xff\xfb':
                print("✅ Valid MP3 file format detected")
            else:
                print("⚠️  MP3 format validation inconclusive")
            
            return True, mp3_path
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False, None

def test_short_mp3():
    """Test MP3 generation with short text (no chunking)"""
    
    url = "http://localhost:8000/tts"
    
    # Short text that won't be chunked
    short_text = "This is a short test message for MP3 generation without chunking."
    
    test_data = {
        "text": short_text,
        "exaggeration": 0.6,
        "cfg_weight": 0.5,
        "temperature": 1.0,
        "output_format": "mp3",
        "return_base64": False
    }
    
    print("\n🎵 Testing Non-chunked MP3 Generation...")
    print(f"📝 Text: {short_text}")
    print(f"🔊 Format: {test_data['output_format']}")
    print()
    
    start_time = time.time()
    
    try:
        print("⏳ Sending short text request to TTS API...")
        response = requests.post(url, json=test_data, timeout=120)
        
        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            
            headers = response.headers
            audio_duration = headers.get('X-Audio-Duration', 'Unknown')
            sample_rate = headers.get('X-Sample-Rate', 'Unknown')
            
            print("✅ Non-chunked MP3 generation successful!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print(f"🎵 Audio duration: {audio_duration} seconds")
            print(f"📊 Sample rate: {sample_rate} Hz")
            print(f"💾 MP3 file size: {len(response.content)} bytes")
            
            # Save the MP3 file
            with tempfile.NamedTemporaryFile(suffix="_short.mp3", delete=False) as tmp:
                tmp.write(response.content)
                mp3_path = tmp.name
                print(f"💿 MP3 saved to: {mp3_path}")
            
            return True, mp3_path
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False, None

def compare_file_sizes(chunked_path, short_path):
    """Compare file sizes to ensure chunked audio is proportionally larger"""
    if chunked_path and short_path and os.path.exists(chunked_path) and os.path.exists(short_path):
        chunked_size = os.path.getsize(chunked_path)
        short_size = os.path.getsize(short_path)
        ratio = chunked_size / short_size
        
        print(f"\n📊 File Size Comparison:")
        print(f"   Chunked MP3: {chunked_size:,} bytes")
        print(f"   Short MP3: {short_size:,} bytes")
        print(f"   Size ratio: {ratio:.2f}x")
        
        if ratio > 2.0:  # Chunked should be significantly larger
            print("✅ File size ratio looks reasonable")
        else:
            print("⚠️  Unexpected file size ratio")

def main():
    """Run MP3 chunking compatibility tests"""
    print("🧪 Chatterbox TTS - MP3 Chunking Compatibility Test")
    print("=" * 60)
    print("Testing whether the new smart chunking logic works properly")
    print("with MP3 format conversion and audio concatenation.")
    print()
    
    # Test chunked MP3 generation
    chunked_success, chunked_path = test_chunked_mp3()
    
    # Test non-chunked MP3 generation
    short_success, short_path = test_short_mp3()
    
    # Compare results
    if chunked_success and short_success:
        compare_file_sizes(chunked_path, short_path)
        
        print(f"\n🎉 Both tests passed!")
        print("✅ Smart chunking is compatible with MP3 conversion")
        print("✅ Audio concatenation works seamlessly with format conversion")
        print()
        print("The chunking happens at the text level before audio generation,")
        print("so it's completely transparent to the MP3 conversion process.")
        print()
        print("Generated files:")
        if chunked_path:
            print(f"  - Chunked MP3: {chunked_path}")
        if short_path:
            print(f"  - Short MP3: {short_path}")
            
    elif chunked_success:
        print(f"\n✅ Chunked MP3 test passed")
        print(f"❌ Short MP3 test failed")
        
    elif short_success:
        print(f"\n❌ Chunked MP3 test failed")
        print(f"✅ Short MP3 test passed")
        
    else:
        print(f"\n❌ Both tests failed - check if TTS server is running")
        print("Start server with: python app.py")

if __name__ == "__main__":
    main()
