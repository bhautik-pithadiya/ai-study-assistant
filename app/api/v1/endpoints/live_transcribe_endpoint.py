from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.models.schemas import LiveTranscribeRequest, LiveTranscribeResponse
from app.services.transcribe_service import TranscribeService
from app.utils.utils import m4a_to_wav_mono_bytes
import os

router = APIRouter(
    prefix="/transcribe",
    tags=["transcribe"],
    responses={404: {"description": "Not found"}},
)

transcribe_service = TranscribeService()

@router.post('/test-upload', response_model=LiveTranscribeResponse)
async def test_transcribe_upload(file: UploadFile = File(...)):
    """Test endpoint: Upload an audio file and get transcription."""
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Read file content as bytes
        audio_content = await file.read()
                
        # Get transcription
        transcript,confidence = transcribe_service.transcribe(audio_content)
        
        return LiveTranscribeResponse(
            transcript=transcript,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe", response_model=LiveTranscribeResponse)
async def live_transcribe(request: LiveTranscribeRequest):
    """Transcribe live audio stream."""
    try:
        # Convert audio content to bytes if it's not already
        audio_bytes = bytes(request.audio_content)
        transcript = await transcribe_service.transcribe(audio_bytes)
        return LiveTranscribeResponse(
            transcript=transcript,
            confidence=1.0  # TODO: Implement confidence calculation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 