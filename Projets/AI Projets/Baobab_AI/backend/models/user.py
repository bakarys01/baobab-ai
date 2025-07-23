"""User models for Baobab AI Labs community features."""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMIN = "admin"

class AfricanCountry(str, Enum):
    NIGERIA = "nigeria"
    SOUTH_AFRICA = "south_africa"
    KENYA = "kenya"
    GHANA = "ghana"
    ETHIOPIA = "ethiopia"
    MOROCCO = "morocco"
    EGYPT = "egypt"
    UGANDA = "uganda"
    TANZANIA = "tanzania"
    ALGERIA = "algeria"
    OTHER = "other"

class UserProfile(BaseModel):
    id: Optional[str] = Field(None, description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    country: AfricanCountry = Field(..., description="African country")
    city: Optional[str] = Field(None, max_length=100, description="City")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    role: UserRole = Field(UserRole.USER, description="User role")
    preferred_language: str = Field("en", description="Preferred language (en, fr, sw, etc.)")
    
    # Professional info
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    experience_level: Optional[str] = Field(None, description="AI experience level")
    
    # Interests and expertise
    ai_interests: List[str] = Field(default_factory=list, description="AI interest areas")
    skills: List[str] = Field(default_factory=list, description="Technical skills")
    
    # Activity tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    tutorial_progress: Dict[str, Any] = Field(default_factory=dict)
    contribution_count: int = Field(0, description="Number of contributions")
    
    @validator('ai_interests', 'skills')
    def validate_lists(cls, v):
        if len(v) > 20:  # Reasonable limit
            raise ValueError('Too many items in list')
        return [item.lower().strip() for item in v if item.strip()]
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()

class UserRegistration(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, description="Password")
    country: AfricanCountry
    city: Optional[str] = None
    preferred_language: str = "en"
    company: Optional[str] = None
    job_title: Optional[str] = None
    ai_interests: List[str] = Field(default_factory=list)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    experience_level: Optional[str] = None
    ai_interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    preferred_language: Optional[str] = None

class UserStats(BaseModel):
    total_users: int
    users_by_country: Dict[str, int]
    active_users_last_30_days: int
    top_contributors: List[Dict[str, Any]]
    most_popular_interests: List[Dict[str, int]]