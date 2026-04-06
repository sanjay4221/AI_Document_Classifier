from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model": settings.GROQ_MODEL,
        "departments": settings.DEPARTMENTS,
    }
