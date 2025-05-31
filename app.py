from fastapi import FastAPI, Response, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import torchaudio as ta
import torch
import tempfile
import os
import base64
import logging
import asyncio
import uuid
from datetime import datetime
from enum import Enum
from chatterbox.tts import ChatterboxTTS
import subprocess
import shutil
import re
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple job data structure for queue processing
class TTSJob:
    def __init__(self, job_id: str, request_data: dict, audio_file_path: Optional[str] = None):
        self.job_id = job_id
        self.request_data = request_data
        self.audio_file_path = audio_file_path
        self.future: Optional[asyncio.Future] = None

# Global queue for processing
job_queue = asyncio.Queue()
total_jobs_processed = 0

# Audio generation limits
COMFORTABLE_DURATION = 25.0  # Target duration for optimal quality
MAX_DURATION_HARD_LIMIT = 40.0  # Hard limit - must chunk beyond this
ESTIMATED_CHARS_PER_SECOND = 12  # Rough estimate for duration calculation

app = FastAPI(
    title="Chatterbox TTS API",
    description="Advanced Text-to-Speech API with voice cloning and emotion control",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically detect GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# Initialize model lazily
model = None

def get_model():
    """Lazy load the model when first needed"""
    global model
    if model is None:
        try:
            logger.info("Loading Chatterbox TTS model...")
            model = ChatterboxTTS.from_pretrained(device=device)
            logger.info("Chatterbox TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    return model

# Queue consumer - single worker processing jobs
async def queue_consumer():
    """Single consumer that processes TTS jobs sequentially"""
    global total_jobs_processed
    logger.info("Starting TTS queue consumer")

    while True:
        try:
            # Get next job from queue
            job: TTSJob = await job_queue.get()

            try:
                # Process the job
                result = await process_job(job)

                # Resolve the future if it exists
                if job.future and not job.future.done():
                    job.future.set_result(result)

                total_jobs_processed += 1

            except Exception as e:
                # Reject the future if it exists
                if job.future and not job.future.done():
                    job.future.set_exception(e)
                logger.error(f"Job {job.job_id} failed: {e}")

            finally:
                # Mark task as done
                job_queue.task_done()

        except Exception as e:
            logger.error(f"Queue consumer error: {e}")
            await asyncio.sleep(1)  # Brief pause before retrying

# Unified job processing function
async def process_job(job: TTSJob) -> dict:
    """Process any type of TTS job"""
    req_data = job.request_data

    # Handle batch processing
    if "texts" in req_data:
        return await _process_batch_job(job)

    # Generate audio (with or without voice cloning)
    audio_prompt_path = job.audio_file_path if job.audio_file_path else None
    wav = _generate_audio(
        text=req_data["text"],
        exaggeration=req_data.get("exaggeration", 0.5),
        cfg_weight=req_data.get("cfg_weight", 0.5),
        temperature=req_data.get("temperature", 1.0),
        audio_prompt_path=audio_prompt_path
    )

    # Clean up uploaded audio file if it exists
    if job.audio_file_path and os.path.exists(job.audio_file_path):
        os.unlink(job.audio_file_path)

    # Calculate duration
    model_instance = get_model()
    duration = _get_audio_duration(wav, model_instance.sr)

    if req_data.get("return_base64", False):
        # Return base64 encoded audio
        audio_b64 = _audio_to_base64(wav, model_instance.sr)
        return {
            "success": True,
            "audio_base64": audio_b64,
            "sample_rate": model_instance.sr,
            "duration_seconds": duration,
            "job_id": job.job_id,
            "voice_cloned": bool(audio_prompt_path)
        }
    else:
        # Convert to requested format and save to temporary file
        output_format = req_data.get("output_format", "wav")
        audio_bytes, media_type = _convert_audio_format(wav, model_instance.sr, output_format)

        # Save converted audio to temporary file
        file_extension = output_format if output_format in ["wav", "mp3", "ogg"] else "wav"
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp:
            tmp.write(audio_bytes)
            return {
                "success": True,
                "audio_file_path": tmp.name,
                "media_type": media_type,
                "sample_rate": model_instance.sr,
                "duration_seconds": duration,
                "job_id": job.job_id,
                "exaggeration": req_data.get("exaggeration", 0.5),
                "cfg_weight": req_data.get("cfg_weight", 0.5),
                "output_format": output_format,
                "voice_cloned": bool(audio_prompt_path)
            }

async def _process_batch_job(job: TTSJob) -> dict:
    """Process a batch TTS job"""
    req_data = job.request_data
    texts = req_data["texts"]

    results = []
    total_duration = 0.0

    for i, text in enumerate(texts):
        try:
            # Generate audio for each text
            wav = _generate_audio(
                text=text,
                exaggeration=req_data.get("exaggeration", 0.5),
                cfg_weight=req_data.get("cfg_weight", 0.5),
                temperature=req_data.get("temperature", 1.0)
            )

            # Calculate duration
            model_instance = get_model()
            duration = _get_audio_duration(wav, model_instance.sr)
            total_duration += duration

            # Convert to base64 (batch always returns base64)
            audio_b64 = _audio_to_base64(wav, model_instance.sr)

            results.append({
                "success": True,
                "audio_base64": audio_b64,
                "sample_rate": model_instance.sr,
                "duration_seconds": duration
            })

        except Exception as e:
            logger.error(f"Failed to process batch text {i}: {e}")
            results.append({
                "success": False,
                "message": str(e),
                "sample_rate": 22050,  # Default sample rate
                "duration_seconds": 0.0
            })

    return {
        "success": True,
        "results": results,
        "total_duration": total_duration,
        "job_id": job.job_id
    }

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", max_length=1000)
    exaggeration: float = Field(0.5, description="Controls emotional intensity", ge=0.0, le=2.0)
    cfg_weight: float = Field(0.5, description="Controls generation guidance", ge=0.0, le=1.0)
    temperature: float = Field(1.0, description="Controls randomness", ge=0.1, le=2.0)
    output_format: str = Field("wav", description="Output audio format", pattern="^(wav|mp3|ogg)$")
    return_base64: bool = Field(False, description="Return audio as base64 encoded string")

class BatchTTSRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to convert", max_items=10)
    exaggeration: float = Field(0.5, description="Controls emotional intensity", ge=0.0, le=2.0)
    cfg_weight: float = Field(0.5, description="Controls generation guidance", ge=0.0, le=1.0)
    temperature: float = Field(1.0, description="Controls randomness", ge=0.1, le=2.0)

class TTSResponse(BaseModel):
    success: bool
    audio_base64: Optional[str] = None
    message: Optional[str] = None
    sample_rate: int
    duration_seconds: float
    job_id: Optional[str] = None

class BatchTTSResponse(BaseModel):
    success: bool
    results: List[TTSResponse]
    total_duration: float
    job_id: Optional[str] = None

# Startup event to start the queue consumer
@app.on_event("startup")
async def startup_event():
    """Start the queue consumer on startup"""
    asyncio.create_task(queue_consumer())
    logger.info("Queue consumer started")

# Helper function for job submission
async def submit_job_and_wait(job: TTSJob, timeout: float = 300.0) -> dict:
    """Submit a job to the queue and wait for completion"""
    # Create a future for this job
    job.future = asyncio.Future()

    # Submit job to queue
    await job_queue.put(job)

    try:
        # Wait for completion with timeout
        result = await asyncio.wait_for(job.future, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Chatterbox TTS API is running",
        "version": "1.1.0",
        "device": device,
        "model_loaded": model is not None,
        "queue_size": job_queue.qsize(),
        "total_jobs_processed": total_jobs_processed
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test model with a simple generation (this will load the model if not loaded)
        model_instance = get_model()
        test_wav = model_instance.generate("Test", exaggeration=0.5, cfg_weight=0.5)
        return {
            "status": "healthy",
            "device": device,
            "model_loaded": True,
            "gpu_available": torch.cuda.is_available(),
            "sample_rate": model_instance.sr
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

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

def _concatenate_audio_files(audio_files: List[str], output_path: str, sample_rate: int) -> None:
    """Concatenate multiple audio files using ffmpeg"""
    if not audio_files:
        raise ValueError("No audio files to concatenate")
    
    if len(audio_files) == 1:
        # Just copy the single file
        shutil.copy2(audio_files[0], output_path)
        return
    
    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for audio concatenation but not found in PATH")
    
    try:
        # Create a temporary file list for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filelist_path = f.name
            for audio_file in audio_files:
                # Escape paths for ffmpeg
                escaped_path = audio_file.replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")
        
        # Use ffmpeg to concatenate
        subprocess.run([
            "ffmpeg", 
            "-f", "concat", 
            "-safe", "0",
            "-i", filelist_path,
            "-c", "copy",
            "-y", output_path
        ], check=True, capture_output=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg concatenation failed: {e.stderr.decode()}")
        raise RuntimeError(f"Audio concatenation failed: {e.stderr.decode()}")
    finally:
        # Clean up filelist
        if os.path.exists(filelist_path):
            os.unlink(filelist_path)

def _generate_audio(text: str, exaggeration: float = 0.5, cfg_weight: float = 0.5,
                   temperature: float = 1.0, audio_prompt_path: Optional[str] = None):
    """Helper function to generate audio with automatic chunking for long texts"""
    try:
        # Check if text needs chunking
        estimated_duration = _estimate_audio_duration(text)
        
        if estimated_duration <= MAX_DURATION_HARD_LIMIT:
            # Text is manageable, generate normally (even if over comfortable duration)
            kwargs = {
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "temperature": temperature
            }
            
            if audio_prompt_path:
                kwargs["audio_prompt_path"] = audio_prompt_path
            
            wav = get_model().generate(text, **kwargs)
            return wav
        
        else:
            # Text is definitely too long, chunk it
            logger.info(f"Text estimated at {estimated_duration:.1f}s, chunking for audio generation")
            chunks = _chunk_text_smartly(text, COMFORTABLE_DURATION)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Generate audio for each chunk
            temp_audio_files = []
            model_instance = get_model()
            
            try:
                for i, chunk in enumerate(chunks):
                    logger.info(f"Generating chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
                    
                    kwargs = {
                        "exaggeration": exaggeration,
                        "cfg_weight": cfg_weight,
                        "temperature": temperature
                    }
                    
                    # Only use audio prompt for the first chunk to maintain voice consistency
                    if audio_prompt_path and i == 0:
                        kwargs["audio_prompt_path"] = audio_prompt_path
                    
                    chunk_wav = model_instance.generate(chunk, **kwargs)
                    
                    # Save chunk to temporary file
                    with tempfile.NamedTemporaryFile(suffix=f"_chunk_{i}.wav", delete=False) as tmp:
                        ta.save(tmp.name, chunk_wav, model_instance.sr)
                        temp_audio_files.append(tmp.name)
                
                # Concatenate all chunks
                with tempfile.NamedTemporaryFile(suffix="_concatenated.wav", delete=False) as tmp:
                    concatenated_path = tmp.name
                
                logger.info(f"Concatenating {len(temp_audio_files)} audio chunks")
                _concatenate_audio_files(temp_audio_files, concatenated_path, model_instance.sr)
                
                # Load the concatenated audio
                concatenated_wav, _ = ta.load(concatenated_path)
                
                # Clean up concatenated temp file
                os.unlink(concatenated_path)
                
                return concatenated_wav
                
            finally:
                # Clean up all temporary chunk files
                for temp_file in temp_audio_files:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

def _audio_to_base64(wav_tensor, sample_rate: int) -> str:
    """Convert audio tensor to base64 string"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        ta.save(tmp.name, wav_tensor, sample_rate)
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp.name)
        return base64.b64encode(audio_bytes).decode('utf-8')

def _get_audio_duration(wav_tensor, sample_rate: int) -> float:
    """Calculate audio duration in seconds"""
    return wav_tensor.shape[-1] / sample_rate

def _convert_audio_format(wav_tensor, sample_rate: int, output_format: str) -> tuple[bytes, str]:
    """Convert audio tensor to different formats"""
    # First save as WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_tmp:
        ta.save(wav_tmp.name, wav_tensor, sample_rate)
        wav_path = wav_tmp.name

    try:
        if output_format.lower() == "wav":
            with open(wav_path, "rb") as f:
                audio_bytes = f.read()
            return audio_bytes, "audio/wav"

        elif output_format.lower() == "mp3":
            # Convert WAV to MP3 using ffmpeg
            mp3_path = wav_path.replace(".wav", ".mp3")

            # Check if ffmpeg is available
            if not shutil.which("ffmpeg"):
                logger.warning("ffmpeg not found, returning WAV instead of MP3")
                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_bytes, "audio/wav"

            try:
                # Convert to MP3
                subprocess.run([
                    "ffmpeg", "-i", wav_path, "-codec:a", "libmp3lame",
                    "-b:a", "128k", "-y", mp3_path
                ], check=True, capture_output=True)

                with open(mp3_path, "rb") as f:
                    audio_bytes = f.read()

                # Clean up MP3 file
                os.unlink(mp3_path)
                return audio_bytes, "audio/mpeg"

            except subprocess.CalledProcessError as e:
                logger.error(f"ffmpeg conversion failed: {e}")
                # Fallback to WAV
                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_bytes, "audio/wav"

        elif output_format.lower() == "ogg":
            # Convert WAV to OGG using ffmpeg
            ogg_path = wav_path.replace(".wav", ".ogg")

            if not shutil.which("ffmpeg"):
                logger.warning("ffmpeg not found, returning WAV instead of OGG")
                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_bytes, "audio/wav"

            try:
                # Convert to OGG
                subprocess.run([
                    "ffmpeg", "-i", wav_path, "-codec:a", "libvorbis",
                    "-q:a", "4", "-y", ogg_path
                ], check=True, capture_output=True)

                with open(ogg_path, "rb") as f:
                    audio_bytes = f.read()

                # Clean up OGG file
                os.unlink(ogg_path)
                return audio_bytes, "audio/ogg"

            except subprocess.CalledProcessError as e:
                logger.error(f"ffmpeg conversion failed: {e}")
                # Fallback to WAV
                with open(wav_path, "rb") as f:
                    audio_bytes = f.read()
                return audio_bytes, "audio/wav"

        else:
            # Unknown format, return WAV
            with open(wav_path, "rb") as f:
                audio_bytes = f.read()
            return audio_bytes, "audio/wav"

    finally:
        # Clean up WAV file
        if os.path.exists(wav_path):
            os.unlink(wav_path)

@app.post("/tts")
async def tts(req: TTSRequest):
    """Text-to-Speech with emotion control and multiple output formats"""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = TTSJob(job_id=job_id, request_data=req.dict())

        # Submit job and wait for completion
        result = await submit_job_and_wait(job)

        if req.return_base64:
            # Return JSON response
            return TTSResponse(
                success=result["success"],
                audio_base64=result.get("audio_base64"),
                sample_rate=result["sample_rate"],
                duration_seconds=result["duration_seconds"],
                job_id=job_id
            )
        else:
            # Return binary audio response
            audio_file_path = result["audio_file_path"]
            media_type = result.get("media_type", "audio/wav")
            output_format = result.get("output_format", "wav")

            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
            os.unlink(audio_file_path)  # Clean up temp file

            return Response(
                content=audio_bytes,
                media_type=media_type,
                headers={
                    "X-Audio-Duration": str(result["duration_seconds"]),
                    "X-Sample-Rate": str(result["sample_rate"]),
                    "X-Exaggeration": str(result["exaggeration"]),
                    "X-CFG-Weight": str(result["cfg_weight"]),
                    "X-Job-ID": job_id,
                    "X-Output-Format": output_format,
                    "X-Voice-Cloned": str(result.get("voice_cloned", False))
                }
            )

    except Exception as e:
        logger.error(f"TTS request failed: {e}")
        if req.return_base64:
            return TTSResponse(
                success=False,
                message=str(e),
                sample_rate=22050,
                duration_seconds=0.0
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-clone")
async def voice_clone(
    text: str,
    audio_file: UploadFile = File(...),
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
    temperature: float = 1.0,
    output_format: str = "wav",
    return_base64: bool = False
):
    """Text-to-Speech with voice cloning from uploaded audio reference"""
    try:
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")

        # Save uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            audio_prompt_path = tmp.name

        # Create job
        job_id = str(uuid.uuid4())
        job = TTSJob(
            job_id=job_id,
            request_data={
                "text": text,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "temperature": temperature,
                "output_format": output_format,
                "return_base64": return_base64
            },
            audio_file_path=audio_prompt_path
        )

        # Submit job and wait for completion
        result = await submit_job_and_wait(job)

        if return_base64:
            # Return JSON response
            return TTSResponse(
                success=result["success"],
                audio_base64=result.get("audio_base64"),
                sample_rate=result["sample_rate"],
                duration_seconds=result["duration_seconds"],
                job_id=job_id
            )
        else:
            # Return binary audio response
            audio_file_path = result["audio_file_path"]
            media_type = result.get("media_type", "audio/wav")
            output_format = result.get("output_format", "wav")

            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
            os.unlink(audio_file_path)  # Clean up temp file

            return Response(
                content=audio_bytes,
                media_type=media_type,
                headers={
                    "X-Audio-Duration": str(result["duration_seconds"]),
                    "X-Sample-Rate": str(result["sample_rate"]),
                    "X-Voice-Cloned": "true",
                    "X-Job-ID": job_id,
                    "X-Output-Format": output_format
                }
            )

    except Exception as e:
        logger.error(f"Voice cloning request failed: {e}")
        if return_base64:
            return TTSResponse(
                success=False,
                message=str(e),
                sample_rate=22050,
                duration_seconds=0.0
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-tts")
async def batch_tts(req: BatchTTSRequest):
    """Batch Text-to-Speech processing for multiple texts"""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = TTSJob(job_id=job_id, request_data=req.dict())

        # Submit job and wait for completion (longer timeout for batch)
        result = await submit_job_and_wait(job, timeout=600.0)

        return BatchTTSResponse(
            success=result["success"],
            results=[TTSResponse(**r) for r in result["results"]],
            total_duration=result["total_duration"],
            job_id=job_id
        )

    except Exception as e:
        logger.error(f"Batch TTS request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple queue status endpoint
@app.get("/queue/status")
async def get_queue_status():
    """Get current queue status"""
    return {
        "queue_size": job_queue.qsize(),
        "total_jobs_processed": total_jobs_processed
    }
