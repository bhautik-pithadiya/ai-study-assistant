from pydantic import BaseModel

class AnswerResponse(BaseModel):
    """Response model for the answer endpoint"""
    answer: str

class MultimodalRequest(BaseModel):
    """Request model for multimodal endpoint"""
    text: str = "" 

class LiveTranscribeRequest(BaseModel):
    audio_content: str
    audio_mime_type: str = "audio/webm;codecs=opus"


class TranscribeResponse(BaseModel):
    """Response model for live transcribe endpoint"""
    transcript: str
    confidence: float