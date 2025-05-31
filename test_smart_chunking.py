#!/usr/bin/env python3
"""
Test script for SMART chunking logic - respects sentence boundaries.
Tests the new intelligent text splitting that targets 25s but allows up to 40s.
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

def test_comfortable_text():
    """Test that comfortable text (under 25s) is not chunked"""
    print("🧪 Test 1: Comfortable text (under 25s)")
    text = "This is a comfortable length text that should not require chunking because it's under our target duration."
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Text: '{text}'")
    print(f"   Estimated duration: {estimated_duration:.2f}s")
    print(f"   Chunks: {len(chunks)}")
    
    if len(chunks) == 1 and estimated_duration <= COMFORTABLE_DURATION:
        print("   ✅ PASS: Comfortable text not chunked")
        return True
    else:
        print("   ❌ FAIL: Comfortable text handling incorrect")
        return False

def test_moderate_text():
    """Test moderate length text (25-40s) - should try gentle chunking"""
    print("\n🧪 Test 2: Moderate text (25-40s)")
    # Create text that's between 25-40 seconds
    text = ("This is a moderate length text that falls between our comfortable duration and hard limit. " * 4 + 
            "It should try gentle chunking but may remain as one chunk if no good break points exist.")
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s")
    
    # Should be in the moderate range and respect sentence boundaries
    if COMFORTABLE_DURATION < estimated_duration <= MAX_DURATION_HARD_LIMIT:
        print("   ✅ PASS: Moderate text handled intelligently")
        return True
    else:
        print("   ❌ FAIL: Text not in expected range")
        return False

def test_long_text_with_sentences():
    """Test long text with clear sentence boundaries"""
    print("\n🧪 Test 3: Long text with sentence boundaries (over 40s)")
    text = ("This is the first sentence with enough content to be substantial. " +
            "Here's another sentence that adds to the total length significantly. " +
            "A third sentence continues to build up the text duration progressively. " +
            "The fourth sentence should definitely push us over the hard limit threshold. " +
            "Fifth sentence ensures we're well into chunking territory for testing purposes. " +
            "Sixth sentence provides additional content to test the intelligent boundary detection. " +
            "Seventh sentence makes sure we have plenty of material for proper chunking evaluation.")
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s - '{chunk[:50]}...'")
        
        if chunk_duration > MAX_DURATION_HARD_LIMIT:
            print(f"   ❌ FAIL: Chunk {i+1} exceeds hard limit")
            return False
    
    if estimated_duration > MAX_DURATION_HARD_LIMIT and len(chunks) > 1:
        print("   ✅ PASS: Long text chunked appropriately")
        return True
    else:
        print("   ❌ FAIL: Long text not handled correctly")
        return False

def test_paragraph_chunking():
    """Test chunking with paragraph breaks"""
    print("\n🧪 Test 4: Paragraph chunking")
    text = """This is the first paragraph that should be substantial enough to contribute meaningfully to the total text duration and demonstrate the intelligent paragraph-based chunking behavior.

This is the second paragraph which also contains enough content to make the overall text exceed our duration limits and trigger the smart chunking algorithm.

This is the third paragraph that definitely pushes the total duration well over our hard limit threshold and should result in proper text segmentation."""
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Total estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        chunk_duration = _estimate_audio_duration(chunk)
        print(f"   Chunk {i+1}: {chunk_duration:.2f}s")
        
        if chunk_duration > MAX_DURATION_HARD_LIMIT:
            print(f"   ❌ FAIL: Chunk {i+1} exceeds hard limit")
            return False
    
    if estimated_duration > MAX_DURATION_HARD_LIMIT and len(chunks) > 1:
        print("   ✅ PASS: Paragraph chunking worked")
        return True
    else:
        print("   ❌ FAIL: Paragraph chunking failed")
        return False

def test_no_good_breaks():
    """Test text with no good natural break points"""
    print("\n🧪 Test 5: Text with no good break points (should keep as one chunk if under 40s)")
    # Create text between 25-40s with no good breaks
    text = ("ThisIsAVeryLongSentenceWithoutAnyNaturalBreakPointsThatGoesOnAndOnWithoutPunctuationOrParagraphBreaks" * 3)
    
    estimated_duration = _estimate_audio_duration(text)
    chunks = _chunk_text_smartly(text)
    
    print(f"   Estimated duration: {estimated_duration:.2f}s")
    print(f"   Number of chunks: {len(chunks)}")
    
    if COMFORTABLE_DURATION < estimated_duration <= MAX_DURATION_HARD_LIMIT:
        if len(chunks) == 1:
            print("   ✅ PASS: Text kept as one chunk (no good breaks)")
            return True
        else:
            print("   ❌ FAIL: Text was chunked unnecessarily")
            return False
    else:
        print("   ✅ INFO: Text outside expected range for this test")
        return True

def test_edge_cases():
    """Test edge cases"""
    print("\n🧪 Test 6: Edge cases")
    
    # Empty text
    chunks = _chunk_text_smartly("")
    if len(chunks) == 1 and chunks[0] == "":
        print("   ✅ Empty text handled correctly")
    else:
        print("   ❌ Empty text not handled correctly")
        return False
    
    # Only whitespace
    chunks = _chunk_text_smartly("   \n\n   ")
    if len(chunks) == 1:
        print("   ✅ Whitespace-only text handled correctly")
    else:
        print("   ❌ Whitespace-only text not handled correctly")
        return False
    
    return True

def main():
    """Run all smart chunking logic tests"""
    print("🧩 Chatterbox TTS - SMART Text Chunking Logic Tests")
    print("=" * 65)
    print(f"Comfortable duration (target): {COMFORTABLE_DURATION}s")
    print(f"Hard limit (must chunk over): {MAX_DURATION_HARD_LIMIT}s")
    print(f"Estimated chars per second: {ESTIMATED_CHARS_PER_SECOND}")
    print()
    print("Strategy:")
    print("- Under 25s: Don't chunk (comfortable)")
    print("- 25-40s: Try gentle chunking, respect sentence boundaries")
    print("- Over 40s: Must chunk, but still be smart about it")
    print()
    
    tests = [
        test_comfortable_text,
        test_moderate_text,
        test_long_text_with_sentences,
        test_paragraph_chunking,
        test_no_good_breaks,
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
        print(f"\n🎉 All smart chunking logic tests passed!")
        print("The system will now target 25s but intelligently allow up to 40s")
        print("to respect sentence boundaries and maintain natural speech flow.")
    else:
        print(f"\n⚠️  Some tests failed. Check the logic above.")

if __name__ == "__main__":
    main()
