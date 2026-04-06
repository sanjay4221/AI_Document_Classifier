import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from backend.core.config import settings
from backend.core.logger import logger
from backend.core.limiter import limiter
from backend.core.exceptions import AppException
from backend.db.database import init_db
from backend.api.routes import auth, documents, classify, health, admin

# ── Create FastAPI app ─────────────────────────────────────────
app = FastAPI( 
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Rate limiter ───────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom exception handler ───────────────────────────────────
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# ── Routers ────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(classify.router)
app.include_router(admin.router)

# ── Serve frontend static files ────────────────────────────────
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# ── Startup ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    logger.info("App ready")