from fastapi import APIRouter, Depends
from app.models.chatbot_schema import ChatRequest, ChatResponse, ChatMessage
from app.services.chatbot_service import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return the response."""
    response_text, session_id, history = await chatbot_service.process_message(
        request.message,
        request.session_id
    )
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        history=[ChatMessage(**msg) for msg in history]
    ) 