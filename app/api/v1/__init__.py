from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router
from app.api.v1.endpoints.live_transcribe_endpoint import router as transcribe_router
from app.api.v1.endpoints.transcribe_ws import router as transcribe_ws_router
from app.api.v1.endpoints.multimodel_endpoint import router as multimodel_router

# Create v1 router (no prefix here)
v1_router = APIRouter()

# Register all v1 endpoints with their specific prefixes
# v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
v1_router.include_router(multimodel_router, prefix="/multimodal", tags=["multimodal"])
v1_router.include_router(transcribe_router, prefix="/transcribe", tags=["transcribe"])
v1_router.include_router(transcribe_ws_router,prefix="/transcribe_ws", tags=['transcribe_ws'])
