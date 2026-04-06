from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from backend.db.database import get_db
from backend.db import crud
from backend.core.security import verify_password, create_access_token
from backend.core.limiter import limiter
from backend.core.logger import logger
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
async def me(db: Session = Depends(get_db),
             current_user=Depends(__import__('backend.api.deps', fromlist=['get_current_user']).get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
    }
