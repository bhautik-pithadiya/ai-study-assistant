from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router
from app.api.v1.endpoints.multimodel_endpoint import router as multimodel_router
from app.api.v1.endpoints.live_transcribe_endpoint import router as live_transcribe_router


# Create v1 router
v1_router = APIRouter()

# Register all v1 endpoints
v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
v1_router.include_router(multimodel_router, prefix="/multimodal", tags=["multimodal"])
v1_router.include_router(live_transcribe_router, prefix="/transcribe", tags=["transcribe"])
