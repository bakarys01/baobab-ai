"""Content models for Baobab AI Labs tutorials, guides, and resources."""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    CASE_STUDY = "case_study"
    TOOL_REVIEW = "tool_review"
    BLOG_POST = "blog_post"
    VIDEO = "video"
    WEBINAR = "webinar"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class TutorialStep(BaseModel):
    step_number: int = Field(..., ge=1, description="Step sequence number")
    title: str = Field(..., max_length=200, description="Step title")
    content: str = Field(..., description="Step content (markdown)")
    code_examples: List[Dict[str, str]] = Field(default_factory=list, description="Code examples")
    resources: List[Dict[str, str]] = Field(default_factory=list, description="Additional resources")
    estimated_time: Optional[int] = Field(None, description="Estimated time in minutes")

class Content(BaseModel):
    id: Optional[str] = Field(None, description="Content ID")
    title: str = Field(..., max_length=200, description="Content title")
    slug: str = Field(..., max_length=200, description="URL slug")
    description: str = Field(..., max_length=500, description="Content description")
    content_type: ContentType = Field(..., description="Type of content")
    
    # Content body
    content_body: str = Field(..., description="Main content (markdown)")
    summary: Optional[str] = Field(None, max_length=300, description="Content summary")
    
    # Tutorial specific
    steps: List[TutorialStep] = Field(default_factory=list, description="Tutorial steps")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives")
    
    # Metadata
    author_id: str = Field(..., description="Author user ID")
    author_name: str = Field(..., description="Author display name")
    difficulty_level: DifficultyLevel = Field(..., description="Content difficulty")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    
    # Categorization
    tags: List[str] = Field(default_factory=list, description="Content tags")
    categories: List[str] = Field(default_factory=list, description="Content categories")
    african_countries: List[str] = Field(default_factory=list, description="Relevant African countries")
    languages: List[str] = Field(default_factory=list, description="Content languages")
    
    # External resources
    external_links: List[Dict[str, str]] = Field(default_factory=list, description="External links")
    github_repo: Optional[HttpUrl] = Field(None, description="GitHub repository")
    demo_url: Optional[HttpUrl] = Field(None, description="Demo URL")
    
    # Publishing
    status: ContentStatus = Field(ContentStatus.DRAFT, description="Content status")
    published_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Engagement
    view_count: int = Field(0, description="View count")
    like_count: int = Field(0, description="Like count")
    bookmark_count: int = Field(0, description="Bookmark count")
    completion_rate: float = Field(0.0, description="Tutorial completion rate")
    
    @validator('slug')
    def validate_slug(cls, v):
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug can only contain lowercase letters, numbers, and hyphens')
        return v
    
    @validator('tags', 'categories')
    def validate_tag_lists(cls, v):
        if len(v) > 15:
            raise ValueError('Too many tags/categories')
        return [item.lower().strip() for item in v if item.strip()]

class ContentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=500)
    content_type: ContentType
    content_body: str
    difficulty_level: DifficultyLevel
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = None
    african_countries: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list, description="Default to ['en']")
    external_links: List[Dict[str, str]] = Field(default_factory=list)
    github_repo: Optional[HttpUrl] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    content_body: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    estimated_duration: Optional[int] = None
    status: Optional[ContentStatus] = None

class CaseStudy(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., max_length=200)
    company_name: str = Field(..., max_length=100)
    country: str = Field(..., description="African country")
    industry: str = Field(..., max_length=100)
    
    # Challenge and solution
    challenge: str = Field(..., description="Business challenge faced")
    solution: str = Field(..., description="AI solution implemented")
    implementation: str = Field(..., description="Implementation details")
    results: str = Field(..., description="Results achieved")
    
    # Metrics
    roi_percentage: Optional[float] = Field(None, description="Return on investment %")
    time_saved: Optional[str] = Field(None, description="Time saved description")
    cost_savings: Optional[str] = Field(None, description="Cost savings description")
    
    # Technical details
    technologies_used: List[str] = Field(default_factory=list)
    team_size: Optional[int] = None
    implementation_duration: Optional[str] = None
    budget_range: Optional[str] = None
    
    # Contact and resources
    contact_person: Optional[str] = None
    company_website: Optional[HttpUrl] = None
    case_study_url: Optional[HttpUrl] = None
    
    # Publishing
    author_id: str
    status: ContentStatus = Field(ContentStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Engagement
    view_count: int = Field(0)
    like_count: int = Field(0)
    share_count: int = Field(0)

class ToolReview(BaseModel):
    id: Optional[str] = None
    tool_name: str = Field(..., max_length=100)
    tool_website: HttpUrl
    category: str = Field(..., max_length=50, description="Tool category")
    
    # Review content
    overview: str = Field(..., description="Tool overview")
    pros: List[str] = Field(..., description="Pros")
    cons: List[str] = Field(..., description="Cons")
    use_cases: List[str] = Field(..., description="African business use cases")
    
    # Ratings (1-5 scale)
    ease_of_use: float = Field(..., ge=1, le=5)
    documentation: float = Field(..., ge=1, le=5)
    pricing_value: float = Field(..., ge=1, le=5)
    african_suitability: float = Field(..., ge=1, le=5, description="Suitability for African context")
    overall_rating: float = Field(..., ge=1, le=5)
    
    # Pricing and availability
    pricing_model: str = Field(..., description="Pricing model")
    free_tier_available: bool = Field(False)
    african_presence: bool = Field(False, description="Has African offices/support")
    local_payment_support: bool = Field(False, description="Supports African payment methods")
    
    # Technical details
    supported_platforms: List[str] = Field(default_factory=list)
    api_available: bool = Field(False)
    integration_complexity: str = Field(..., description="Integration complexity level")
    
    # Publishing
    author_id: str
    reviewed_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: ContentStatus = Field(ContentStatus.DRAFT)

class ContentStats(BaseModel):
    total_content: int
    content_by_type: Dict[str, int]
    content_by_difficulty: Dict[str, int]
    content_by_country: Dict[str, int]
    most_viewed: List[Dict[str, Any]]
    recent_content: List[Dict[str, Any]]
    top_contributors: List[Dict[str, Any]]