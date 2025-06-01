from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router
from app.api.v1.endpoints.multimodel_endpoint import router as multimodel_router
from app.api.v1.endpoints.live_transcribe_endpoint import router as live_transcribe_router
from app.api.v1.endpoints.transcribe_ws import router as transcribe_ws_router


# Create the main API router
api_router = APIRouter()

# Register v1 routes
v1_router = APIRouter()
# v1_router.include_router(chatbot_router, tags=["chatbot"])
v1_router.include_router(multimodel_router, prefix="/multimodal", tags=["multimodal"])
v1_router.include_router(live_transcribe_router, tags=["transcribe"])
v1_router.include_router(transcribe_ws_router,prefix="/transcribe_ws", tags=['transcribe_ws'])

# Include v1 router in the main API router
api_router.include_router(v1_router)