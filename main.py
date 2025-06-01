from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.config.settings import settings
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    logger.info("Creating FastAPI application")
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="API for answering academic questions using Gemini's multimodal capabilities",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    logger.info("Configuring CORS middleware")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    logger.info("Including API router")
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

# Create FastAPI application
app = create_application()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server")

    uvicorn.run(app, host="0.0.0.0", port=8000)