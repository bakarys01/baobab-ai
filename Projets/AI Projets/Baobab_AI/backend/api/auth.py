"""Authentication and user management API endpoints with database integration."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.user import UserProfile, UserRegistration, UserLogin, UserUpdate
from services.database_service import UserService
from database import get_db
from jose import JWTError, jwt
import os

router = APIRouter()
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserService.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegistration, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        # Create new user
        user = UserService.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            country=user_data.country,
            profession=user_data.job_title,
            interests=user_data.ai_interests
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = UserService.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "country": user.country,
                "profession": user.profession,
                "created_at": user.created_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    user = UserService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = UserService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "country": user.country,
            "profession": user.profession,
            "created_at": user.created_at.isoformat()
        }
    )

@router.get("/me")
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "country": current_user.country,
        "profession": current_user.profession,
        "experience_level": current_user.experience_level,
        "interests": current_user.interests,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }

@router.put("/me")
async def update_user_profile(
    user_updates: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    update_data = user_updates.dict(exclude_unset=True)
    
    updated_user = UserService.update_user(db, current_user.id, **update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "country": updated_user.country,
        "profession": updated_user.profession,
        "experience_level": updated_user.experience_level,
        "interests": updated_user.interests,
        "updated_at": updated_user.updated_at.isoformat()
    }

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user (client should discard token)."""
    return {"message": f"User {current_user.username} successfully logged out"}

@router.get("/users/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """Get user statistics (public endpoint)."""
    # This would need to be implemented with proper database queries
    # For now, return basic stats
    return {
        "total_users": 0,
        "users_by_country": {},
        "active_users_last_30_days": 0
    }