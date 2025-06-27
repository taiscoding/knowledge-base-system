"""
Voice API
Endpoints for speech-to-text processing and voice input.
"""

import os
import tempfile
import uuid
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, WebSocket, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import speech_recognition as sr
import logging

from services.kb_service import KnowledgeBaseService, get_kb_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Global recognizer
recognizer = sr.Recognizer()

@router.post("/transcribe", response_model=Dict[str, Any])
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en-US"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Transcribe audio file to text.
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            # Write file contents
            content = await audio_file.read()
            temp_file.write(content)
        
        # Process with speech recognition
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)
        
        # Delete temporary file
        os.unlink(temp_file_path)
        
        return {
            "success": True, 
            "text": text
        }
    except sr.UnknownValueError:
        return {
            "success": False,
            "error": "Speech recognition could not understand audio"
        }
    except sr.RequestError as e:
        return {
            "success": False,
            "error": f"Could not request results from speech recognition service: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Ensure temporary file is deleted
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

@router.post("/process-voice", response_model=Dict[str, Any])
async def process_voice(
    audio_file: UploadFile = File(...),
    language: str = Form("en-US"),
    session_id: Optional[str] = Form(None),
    privacy_level: str = Form("balanced"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Process voice input by transcribing and then processing the text.
    """
    try:
        # First transcribe the audio
        transcription_result = await transcribe_audio(audio_file, language)
        
        if not transcription_result["success"]:
            return transcription_result
            
        # Process the transcribed text
        text = transcription_result["text"]
        
        # Process with privacy if session_id is provided
        if session_id:
            result = kb_service.process_with_privacy(text, session_id, privacy_level)
        else:
            result = kb_service.process_stream_of_consciousness(text)
            
        return {
            "success": True,
            "transcription": text,
            "processing_result": result
        }
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@router.websocket("/stream")
async def voice_stream(
    websocket: WebSocket,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Stream audio data for real-time transcription and processing.
    """
    await websocket.accept()
    
    # Create a session ID for this connection
    session_id = str(uuid.uuid4())
    buffer = bytearray()
    
    try:
        # Send initial confirmation
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Voice streaming connection established"
        })
        
        while True:
            # Receive binary data (audio chunks)
            data = await websocket.receive_bytes()
            
            # Add to buffer
            buffer.extend(data)
            
            # Check if we have enough data to process (e.g., 2 seconds of audio)
            # This is simplified - real implementation would need proper audio framing
            if len(buffer) >= 32000:  # ~2 seconds at 16kHz, 16-bit
                # Process audio chunk
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(buffer)
                
                try:
                    # Process with speech recognition
                    with sr.AudioFile(temp_file_path) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                        
                        # Send transcription to client
                        await websocket.send_json({
                            "type": "transcription",
                            "text": text
                        })
                        
                        # Process transcription if it's substantial
                        if len(text.strip().split()) > 3:  # More than 3 words
                            result = kb_service.process_stream_of_consciousness(text)
                            
                            # Send processing result to client
                            await websocket.send_json({
                                "type": "processing_result",
                                "result": result
                            })
                except sr.UnknownValueError:
                    # No speech detected, send notification
                    await websocket.send_json({
                        "type": "status",
                        "message": "No speech detected"
                    })
                except Exception as e:
                    # Error in processing
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                        except:
                            pass
                
                # Reset buffer
                buffer = bytearray()
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        # Try to send error message if connection is still open
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Stream processing error: {str(e)}"
            })
        except:
            pass 