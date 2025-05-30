from pydantic import BaseModel

class AnswerResponse(BaseModel):
    """Response model for the answer endpoint"""
    answer: str

class MultimodalRequest(BaseModel):
    """Request model for multimodal endpoint"""
    text: str = "" 