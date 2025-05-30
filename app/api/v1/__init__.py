from fastapi import APIRouter
from app.api.v1.endpoints.chatbot_endpoint import router as chatbot_router

# Create v1 router
v1_router = APIRouter()

# Register all v1 endpoints
v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
