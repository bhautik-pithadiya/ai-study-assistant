from pydantic import BaseModel

class AnswerResponse(BaseModel):
    """Response model for the answer endpoint"""
    answer: str

class MultimodalRequest(BaseModel):
    """Request model for multimodal endpoint"""
    text: str = "" 

class LiveTranscribeRequest(BaseModel):
    """Request model for live transcribe endpoint"""
    audio_content: bytes
    audio_mime_type: str

class LiveTranscribeResponse(BaseModel):
    """Response model for live transcribe endpoint"""
    transcript: str
    confidence: float