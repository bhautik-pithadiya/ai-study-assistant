from fastapi import APIRouter, Depends, HTTPException
from app.models.chatbot_schema import ChatRequest, ChatResponse, ChatMessage
from app.services.chatbot_service import ChatbotService
from typing import List

# Create router with specific prefix and tags
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
chatbot_service = ChatbotService()

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return the response."""
    try:
        response_text, session_id, history = await chatbot_service.process_message(
            request.message,
            request.session_id
        )
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            history=[ChatMessage(**msg) for msg in history]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 