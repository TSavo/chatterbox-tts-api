#!/usr/bin/env python3
"""
Test script for chunking logic only - no TTS API calls required.
Tests the intelligent text splitting algorithms directly.
"""

import re
from typing import List

# Configuration constants
COMFORTABLE_DURATION = 25.0  # Target duration for optimal quality
MAX_DURATION_HARD_LIMIT = 40.0  # Hard limit - must chunk beyond this
ESTIMATED_CHARS_PER_SECOND = 12  # Rough estimate for duration calculation

def _estimate_audio_duration(text: str) -> float:
    """Estimate audio duration based on text length"""
    # Remove extra whitespace and count characters
    clean_text = re.sub(r'\s+', ' ', text.strip())
    char_count = len(clean_text)
    
    # Rough estimation: ~12 characters per second of speech
    estimated_duration = char_count / ESTIMATED_CHARS_PER_SECOND
    return estimated_duration

def _chunk_text_smartly(text: str, comfortable_duration: float = COMFORTABLE_DURATION) -> List[str]:
    """
    Intelligently chunk text with respect for sentence boundaries.
    
    Strategy:
    - Under 25s: Don't chunk (comfortable)
    - 25-40s: Try to find good break points, but don't force chunking
    - Over 40s: Must chunk, but still respect sentence boundaries
    
    Splits on:
    1. Double line breaks (paragraphs)
    2. Single line breaks
    3. Sentence endings (. ! ?) - preferred break points
    4. Clause breaks (, ; :) - only if necessary
    5. Word boundaries - last resort
    """
    estimated_duration = _estimate_audio_duration(text)
    
    # If text is comfortably short, don't chunk
    if estimated_duration <= comfortable_duration:
        return [text.strip()]
    
    # If moderately long but under hard limit, try gentle chunking
    if estimated_duration <= MAX_DURATION_HARD_LIMIT:
        # Try to find natural paragraph or sentence breaks
        gentle_chunks = _try_gentle_chunking(text, comfortable_duration)
        if gentle_chunks and len(gentle_chunks) > 1:
            return gentle_chunks
        else:
            # No good break points found, keep as single chunk
            return [text.strip()]
    
    # Over hard limit - must chunk aggressively but smartly
    return _aggressive_chunking(text, comfortable_duration)

def _try_gentle_chunking(text: str, target_duration: float) -> List[str]:
    """Try to find natural break points without forcing chunking"""
    chunks = []
    
    # First try paragraph breaks
    paragraphs = re.split(r'\n\s*\n', text)
    if len(paragraphs) > 1:
        current_chunk = ""
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            test_chunk = (current_chunk + "\n\n" + paragraph) if current_chunk else paragraph
            
            # If adding this paragraph keeps us reasonable, add it
            if _estimate_audio_duration(test_chunk) <= MAX_DURATION_HARD_LIMIT:
                current_chunk = test_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    # No paragraph breaks, try sentence breaks
    sentences = re.split(r'([.!?]+)', text)
    if len(sentences) > 2:  # At least one sentence break
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]  # Include punctuation
            else:
                sentence = sentences[i]
            
            sentence = sentence.strip()
            if not sentence:
                continue
            
            test_chunk = (current_chunk + " " + sentence) if current_chunk else sentence
            
            # If this sentence would put us way over, break before it
            if current_chunk and _estimate_audio_duration(test_chunk) > MAX_DURATION_HARD_LIMIT:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # Only return if we actually found reasonable break points
        if len(chunks) > 1:
            return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    # No good natural breaks found
    return []

def _aggressive_chunking(text: str, target_duration: float) -> List[str]:
    """Aggressively chunk text that's over the hard limit"""
    chunks = []
    
    # First split on paragraphs (double line breaks)
    paragraphs = re.split(r'\n\s*\n', text)
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # If paragraph is under target, add it
        if _estimate_audio_duration(paragraph) <= target_duration:
            chunks.append(paragraph)
            continue
        
        # If paragraph is moderately long but under hard limit, try to keep it
        if _estimate_audio_duration(paragraph) <= MAX_DURATION_HARD_LIMIT:
            # Try sentence-level splitting first
            sentence_chunks = _split_long_text(paragraph, target_duration)
            chunks.extend(sentence_chunks)
        else:
            # Paragraph is very long, must split aggressively
            para_chunks = _split_long_text(paragraph, target_duration)
            chunks.extend(para_chunks)
    
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def _split_long_text(text: str, max_duration: float) -> List[str]:
    """Split text that's too long on sentence and clause boundaries"""
    if _estimate_audio_duration(text) <= max_duration:
        return [text]
    
    chunks = []
    
    # Split on sentence endings first
    sentences = re.split(r'([.!?]+)', text)
    current_chunk = ""
    
    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]  # Include punctuation
        else:
            sentence = sentences[i]
        
        sentence = sentence.strip()
        if not sentence:
            continue
        
        test_chunk = (current_chunk + " " + sentence) if current_chunk else sentence
        
        if _estimate_audio_duration(test_chunk) <= max_duration:
            current_chunk = test_chunk
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk)
            
            # Check if sentence itself is too long
            if _estimate_audio_duration(sentence) <= max_duration:
                current_chunk = sentence
            else:
                # Split on clause boundaries
                clause_chunks = _split_on_clauses(sentence, max_duration)
                chunks.extend(clause_chunks[:-1])
                current_chunk = clause_chunks[-1]
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def _split_on_clauses(text: str, max_duration: float) -> List[str]:
    """Split text on clause boundaries (commas, semicolons, colons)"""
    if _estimate_audio_duration(text) <= max_duration:
        return [text]
    
    chunks = []
    
    # Split on clause markers
    clauses = re.split(r'([,;:]+)', text)
    current_chunk = ""
    
    for i in range(0, len(clauses), 2):
        if i + 1 < len(clauses):
            clause = clauses[i] + clauses[i + 1]  # Include punctuation
        else:
            clause = clauses[i]
        
        clause = clause.strip()
        if not clause:
            continue
        
        test_chunk = (current_chunk + " " + clause) if current_chunk else clause
        
        if _estimate_audio_duration(test_chunk) <= max_duration:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # Last resort: split on word boundaries
            if _estimate_audio_duration(clause) <= max_duration:
                current_chunk = clause
            else:
                word_chunks = _split_on_words(clause, max_duration)
                chunks.extend(word_chunks[:-1])
                current_chunk = word_chunks[-1]
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def _split_on_words(text: str, max_duration: float) -> List[str]:
    """Split text on word boundaries as last resort"""
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        test_chunk = (current_chunk + " " + word) if current_chunk else word
        
        if _estimate_audio_duration(test_chunk) <= max_duration:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def test_short_text():
    """Test that short text is not chunked"""
    print("🧪 Test 1: Short text (no chunking expected)")
    text = "This is a short text that should not require chunking."
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Text: '{text}'")
    print(f"   Estimated duration: {estimated_duration:.2f}s")
    print(f"   Chunks: {len(chunks)}")
    
    if len(chunks) == 1:
        print("   ✅ PASS: Short text not chunked")
        return True
    else:
        print("   ❌ FAIL: Short text was chunked unnecessarily")
        return False

def test_paragraph_chunking():
    """Test chunking on paragraph boundaries"""
    print("\n🧪 Test 2: Paragraph chunking")
    # Make this text definitely long enough to require chunking
    text = """This is the first paragraph that contains multiple sentences with enough content to make it quite long indeed. We need to ensure this paragraph alone is substantial enough to demonstrate the chunking behavior when combined with other paragraphs in this comprehensive test case.

This is the second paragraph which also has several sentences and should be treated as a separate chunk when the total text is too long for a single generation. This paragraph also needs to be sufficiently long to contribute meaningfully to the total duration estimate.

This is the third paragraph which should definitely push us over the duration limit and trigger intelligent chunking behavior. By the time we reach this paragraph, the total estimated duration should exceed our maximum threshold of forty seconds, resulting in appropriate text segmentation."""
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s - '{chunk[:50]}...'")
        
        if chunk_duration > MAX_DURATION_HARD_LIMIT:
            print(f"   ❌ FAIL: Chunk {i+1} exceeds hard duration limit")
            return False
      if estimated_duration > MAX_DURATION_HARD_LIMIT:
        if len(chunks) > 1:
            print("   ✅ PASS: Long text was chunked appropriately")
            return True
        else:
            print("   ❌ FAIL: Text was long but not chunked")
            return False
    else:
        if len(chunks) == 1:
            print("   ✅ PASS: Text was short enough, no chunking needed")
            return True
        else:
            print("   ❌ FAIL: Short text was chunked unnecessarily")
            return False

def test_sentence_chunking():
    """Test chunking on sentence boundaries"""
    print("\n🧪 Test 3: Sentence chunking")
    text = ("This is a very long paragraph that contains many sentences. " * 15 + 
            "Each sentence adds to the total length. " * 10 + 
            "Eventually this should exceed the duration limit and be split on sentence boundaries!")
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    all_valid = True
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s")
        
        if chunk_duration > MAX_AUDIO_DURATION:
            print(f"   ❌ FAIL: Chunk {i+1} exceeds duration limit")
            all_valid = False
    
    if all_valid and len(chunks) > 1:
        print("   ✅ PASS: Long text chunked without exceeding limits")
        return True
    else:
        print("   ❌ FAIL: Chunking failed")
        return False

def test_clause_chunking():
    """Test chunking on clause boundaries"""
    print("\n🧪 Test 4: Clause chunking")
    text = ("Here is a sentence with many clauses, separated by commas, " +
            "and semicolons; plus some colons: which should provide natural break points, " +
            "allowing the system to split intelligently, maintaining readability, " +
            "while respecting the duration limits, and ensuring smooth audio generation. " * 8)
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    all_valid = True
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s")
        
        if chunk_duration > MAX_AUDIO_DURATION:
            print(f"   ❌ FAIL: Chunk {i+1} exceeds duration limit")
            all_valid = False
    
    if all_valid and len(chunks) > 1:
        print("   ✅ PASS: Clause chunking worked")
        return True
    else:
        print("   ❌ FAIL: Clause chunking failed")
        return False

def test_word_chunking():
    """Test word-level chunking as last resort"""
    print("\n🧪 Test 5: Word chunking (last resort)")
    text = " ".join(["supercalifragilisticexpialidocious"] * 100)  # Very long words
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    all_valid = True
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s")
        
        if chunk_duration > MAX_AUDIO_DURATION + 5:  # Allow some tolerance for word chunks
            print(f"   ❌ FAIL: Chunk {i+1} significantly exceeds duration limit")
            all_valid = False
    
    if all_valid and len(chunks) > 1:
        print("   ✅ PASS: Word chunking worked")
        return True
    else:
        print("   ❌ FAIL: Word chunking failed")
        return False

def test_edge_cases():
    """Test edge cases"""
    print("\n🧪 Test 6: Edge cases")
    
    # Empty text
    chunks = _chunk_text_smartly("")
    if len(chunks) == 0:
        print("   ✅ Empty text handled correctly")
    else:
        print("   ❌ Empty text not handled correctly")
        return False
    
    # Only whitespace
    chunks = _chunk_text_smartly("   \n\n   ")
    if len(chunks) == 0:
        print("   ✅ Whitespace-only text handled correctly")
    else:
        print("   ❌ Whitespace-only text not handled correctly")
        return False
    
    # Single very long word
    long_word = "a" * 1000
    chunks = _chunk_text_smartly(long_word)
    if len(chunks) == 1:  # Should just return as-is since we can't split words further
        print("   ✅ Single long word handled correctly")
    else:
        print("   ❌ Single long word not handled correctly")
        return False
    
    return True

def main():
    """Run all chunking logic tests"""
    print("🧩 Chatterbox TTS - Text Chunking Logic Tests")
    print("=" * 60)
    print(f"Max duration limit: {MAX_AUDIO_DURATION}s")
    print(f"Estimated chars per second: {ESTIMATED_CHARS_PER_SECOND}")
    print()
    
    tests = [
        test_short_text,
        test_paragraph_chunking,
        test_sentence_chunking,
        test_clause_chunking,
        test_word_chunking,
        test_edge_cases
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
            print(f"   ❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All chunking logic tests passed!")
    else:
        print(f"\n⚠️  Some tests failed. Check the logic above.")

if __name__ == "__main__":
    main()
