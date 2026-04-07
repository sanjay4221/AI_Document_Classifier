from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):

    # Email — Resend
    RESEND_API_KEY: str = ""
    EMAIL_FROM:     str = "onboarding@resend.dev"
    APP_BASE_URL: str = ""

    # App
    APP_NAME: str = "AI Document Classifier"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 8

    # Database
    DATABASE_URL: Optional[str] = None  # None = use SQLite locally

    # Pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENV: Optional[str] = "us-east-1"
    PINECONE_INDEX: Optional[str] = "ai-classifier"

    # Classifier
    LLM_CONFIDENCE_THRESHOLD: float = 0.75
    MAX_FILE_SIZE_MB: int = 10

    # Paths
    UPLOAD_DIR: str = "uploads"
    LOG_DIR: str = "logs"
    MODEL_DIR: str = "backend/training/models"

    # Departments
    DEPARTMENTS: list = [
        "Finance",
        "Human Resources",
        "Legal & Regulatory",
        "Licensing & Compliance",
        "IT & Technology",
        "Operations",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
