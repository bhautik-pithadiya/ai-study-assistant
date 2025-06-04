from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Academic Question Answering API"
    
    # Gemini API Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Google Speech-to-Text Settings
    GOOGLE_API_CRED_PATH: str = os.getenv("GOOGLE_API_KEY", "")
    if GOOGLE_API_CRED_PATH:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(Path(GOOGLE_API_CRED_PATH).resolve())

    # Vector Store Settings
    VECTOR_STORE_PATH: str = "vector_store"
    
    # Chat History Settings
    CHAT_HISTORY_DIR: str = "chat_histories"
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 