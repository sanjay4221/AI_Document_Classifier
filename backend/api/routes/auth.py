from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from backend.db.database import get_db
from backend.db import crud
from backend.core.security import verify_password, create_access_token
from backend.core.limiter import limiter
from backend.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email:     EmailStr
    password:  str
    full_name: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str


# ── Existing endpoints (unchanged) ────────────────────────────────────────────

@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, body.email, body.password, body.full_name)
    logger.info(f"New user registered: {user.email}")
    return {"message": "Account created", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id), "email": user.email, "is_admin": user.is_admin})
    logger.info(f"User logged in: {user.email}")
    return {"access_token": token}


@router.get("/me")
async def me(
    db: Session = Depends(get_db),
    current_user=Depends(__import__('backend.api.deps', fromlist=['get_current_user']).get_current_user)
):
    return {
        "id":        current_user.id,
        "email":     current_user.email,
        "full_name": current_user.full_name,
        "is_admin":  current_user.is_admin,
    }


# ── Forgot Password ────────────────────────────────────────────────────────────

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    from backend.core.email import send_password_reset_email
    from backend.core.config import settings

    raw_token, user = crud.create_password_reset_token(db, body.email)

    if raw_token and user:
        reset_url = f"{settings.APP_BASE_URL}/reset-password.html?token={raw_token}"
        sent = await send_password_reset_email(
            to_email=body.email,
            reset_url=reset_url,
            full_name=user.full_name or "",
        )
        if sent:
            logger.info(f"Password reset email sent: {body.email}")
        else:
            logger.error(f"Failed to send reset email: {body.email}")
    else:
        # Email not found — same response, no enumeration
        logger.info(f"Reset requested for unregistered email: {body.email}")

    # Always return 200 — never reveal if email exists
    return {"message": "If that email is registered, a reset link has been sent."}


# ── Reset Password ─────────────────────────────────────────────────────────────

@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    success = crud.reset_password(db, body.token, body.new_password)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Reset link is invalid or has expired. Please request a new one."
        )

    logger.info("Password successfully reset via token")
    return {"message": "Password updated successfully. You can now sign in."}


# ── Verify Reset Token ─────────────────────────────────────────────────────────

@router.get("/verify-reset-token")
async def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """Called by reset-password.html on page load to validate token before showing form."""
    user = crud.verify_reset_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired.")
    return {"valid": True, "email": user.email}