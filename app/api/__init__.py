from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router
from app.api.v1.endpoints.live_transcribe_endpoint import router as transcribe_router
from app.api.v1.endpoints.transcribe_ws import router as transcribe_ws_router
from app.api.v1.endpoints.multimodel_endpoint import router as multimodel_router

from app.api.v1 import v1_router
import logging

logger = logging.getLogger(__name__)

# Create the main API router
logger.info("Creating main API router")
api_router = APIRouter()

# Register v1 routes
logger.info("Creating v1 router and registering endpoints")
v1_router = APIRouter()
# v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
v1_router.include_router(multimodel_router, prefix="/multimodal", tags=["multimodal"])
v1_router.include_router(transcribe_router, prefix="/transcribe", tags=["transcribe"])
v1_router.include_router(transcribe_ws_router,prefix="/transcribe_ws", tags=['transcribe_ws'])
# Include v1 router in the main API router (remove the /v1 prefix here)
logger.info("Including v1 router in main API router")
api_router.include_router(v1_router)
