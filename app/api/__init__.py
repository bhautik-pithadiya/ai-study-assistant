from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router

# Create the main API router
api_router = APIRouter()

# Register v1 routes
v1_router = APIRouter()
v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])

# Include v1 router in the main API router
api_router.include_router(v1_router, prefix="/v1")
