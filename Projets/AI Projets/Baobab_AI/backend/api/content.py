"""Content management API endpoints for tutorials, guides, case studies, and tool reviews."""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from models.content import (
    Content, ContentCreate, ContentUpdate, CaseStudy, ToolReview,
    ContentType, DifficultyLevel, ContentStatus
)
from models.user import UserProfile
from services.content_service import ContentService
from api.auth import get_current_user

router = APIRouter(prefix="/content", tags=["content"])
content_service = ContentService()

@router.post("/tutorials", response_model=dict)
async def create_tutorial(
    tutorial_data: ContentCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new tutorial."""
    tutorial_dict = tutorial_data.dict()
    tutorial_dict.update({
        "author_id": current_user.id,
        "author_name": current_user.full_name,
        "content_type": "tutorial"
    })
    
    tutorial = content_service.create_tutorial(tutorial_dict)
    return {"success": True, "tutorial": tutorial}

@router.get("/tutorials", response_model=List[dict])
async def list_tutorials(
    status: Optional[ContentStatus] = Query(None, description="Filter by status"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    country: Optional[str] = Query(None, description="Filter by African country"),
    language: Optional[str] = Query(None, description="Filter by language"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    limit: int = Query(20, ge=1, le=100, description="Number of tutorials to return"),
    offset: int = Query(0, ge=0, description="Number of tutorials to skip")
):
    """List tutorials with filters."""
    tutorials = content_service.list_content(
        content_type="tutorials",
        status=status,
        author_id=author_id,
        country=country,
        language=language,
        limit=limit,
        offset=offset
    )
    
    # Filter by difficulty if specified
    if difficulty:
        tutorials = [t for t in tutorials if t.get("difficulty_level") == difficulty]
    
    return tutorials

@router.get("/tutorials/{tutorial_id}", response_model=dict)
async def get_tutorial(tutorial_id: str):
    """Get a specific tutorial."""
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    return tutorial

@router.put("/tutorials/{tutorial_id}", response_model=dict)
async def update_tutorial(
    tutorial_id: str,
    tutorial_updates: ContentUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a tutorial."""
    # Check if user owns the tutorial or is admin
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    if tutorial["author_id"] != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this tutorial")
    
    updated_tutorial = content_service.update_content(
        "tutorials", tutorial_id, tutorial_updates.dict(exclude_unset=True)
    )
    
    if not updated_tutorial:
        raise HTTPException(status_code=500, detail="Failed to update tutorial")
    
    return {"success": True, "tutorial": updated_tutorial}

@router.delete("/tutorials/{tutorial_id}")
async def delete_tutorial(
    tutorial_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a tutorial."""
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    if tutorial["author_id"] != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tutorial")
    
    success = content_service.delete_content("tutorials", tutorial_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete tutorial")
    
    return {"success": True, "message": "Tutorial deleted successfully"}

# Case Studies Endpoints
@router.post("/case-studies", response_model=dict)
async def create_case_study(
    case_study_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new case study."""
    case_study_data.update({
        "author_id": current_user.id,
        "content_type": "case_study"
    })
    
    case_study = content_service.create_case_study(case_study_data)
    return {"success": True, "case_study": case_study}

@router.get("/case-studies", response_model=List[dict])
async def list_case_studies(
    status: Optional[str] = Query(None, description="Filter by status"),
    country: Optional[str] = Query(None, description="Filter by country"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List case studies with filters."""
    case_studies = content_service.list_content(
        content_type="case_studies",
        status=status,
        country=country,
        limit=limit,
        offset=offset
    )
    
    # Filter by industry if specified
    if industry:
        case_studies = [cs for cs in case_studies if cs.get("industry", "").lower() == industry.lower()]
    
    return case_studies

@router.get("/case-studies/{case_study_id}", response_model=dict)
async def get_case_study(case_study_id: str):
    """Get a specific case study."""
    case_study = content_service.get_content("case_studies", case_study_id)
    if not case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    return case_study

# Tool Reviews Endpoints
@router.post("/tool-reviews", response_model=dict)
async def create_tool_review(
    review_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new tool review."""
    review_data.update({
        "author_id": current_user.id,
        "content_type": "tool_review"
    })
    
    review = content_service.create_tool_review(review_data)
    return {"success": True, "review": review}

@router.get("/tool-reviews", response_model=List[dict])
async def list_tool_reviews(
    category: Optional[str] = Query(None, description="Filter by tool category"),
    rating_min: Optional[float] = Query(None, ge=1, le=5, description="Minimum overall rating"),
    african_suitable: Optional[bool] = Query(None, description="Filter by African suitability"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List tool reviews with filters."""
    reviews = content_service.list_content(
        content_type="tool_reviews",
        limit=limit,
        offset=offset
    )
    
    # Apply filters
    filtered_reviews = []
    for review in reviews:
        if category and review.get("category", "").lower() != category.lower():
            continue
        if rating_min and review.get("overall_rating", 0) < rating_min:
            continue
        if african_suitable is not None and review.get("african_suitability", 0) < 3.0:
            continue
        filtered_reviews.append(review)
    
    return filtered_reviews

@router.get("/tool-reviews/{review_id}", response_model=dict)
async def get_tool_review(review_id: str):
    """Get a specific tool review."""
    review = content_service.get_content("tool_reviews", review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Tool review not found")
    return review

# Search and Discovery
@router.get("/search", response_model=List[dict])
async def search_content(
    q: str = Query(..., min_length=2, description="Search query"),
    content_types: Optional[List[str]] = Query(None, description="Content types to search"),
    countries: Optional[List[str]] = Query(None, description="Filter by countries"),
    limit: int = Query(20, ge=1, le=50)
):
    """Search content across all types."""
    if not content_types:
        content_types = ["tutorials", "case_studies", "tool_reviews", "guides"]
    
    results = content_service.search_content(
        query=q,
        content_types=content_types,
        countries=countries,
        limit=limit
    )
    
    return results

@router.get("/featured", response_model=List[dict])
async def get_featured_content(
    content_type: Optional[str] = Query(None, description="Specific content type"),
    limit: int = Query(10, ge=1, le=20)
):
    """Get featured content based on engagement metrics."""
    featured = content_service.get_featured_content(content_type, limit)
    return featured

@router.get("/trending", response_model=List[dict])
async def get_trending_content(
    days: int = Query(7, ge=1, le=30, description="Days to look back for trending"),
    limit: int = Query(10, ge=1, le=20)
):
    """Get trending content based on recent activity."""
    # For now, return featured content
    # In production, this would analyze recent views, likes, etc.
    return content_service.get_featured_content(limit=limit)

@router.get("/categories", response_model=List[str])
async def get_content_categories():
    """Get all available content categories."""
    return [
        "business-ai", "nlp", "computer-vision", "machine-learning",
        "data-science", "agriculture-ai", "fintech-ai", "healthcare-ai",
        "education-ai", "mlops", "cloud-deployment", "mobile-ai"
    ]

@router.get("/tags", response_model=List[str])
async def get_popular_tags():
    """Get popular content tags."""
    return [
        "python", "tensorflow", "pytorch", "chatbot", "api",
        "mobile", "whatsapp", "sms", "agriculture", "fintech",
        "healthcare", "education", "startup", "sme", "cloud",
        "aws", "google-cloud", "azure", "deployment"
    ]

@router.get("/stats", response_model=dict)
async def get_content_stats():
    """Get content statistics."""
    return content_service.get_content_stats()

# Content Interaction Endpoints
@router.post("/tutorials/{tutorial_id}/like")
async def like_tutorial(
    tutorial_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Like a tutorial."""
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Increment like count
    tutorial["like_count"] = tutorial.get("like_count", 0) + 1
    content_service.update_content("tutorials", tutorial_id, {"like_count": tutorial["like_count"]})
    
    return {"success": True, "likes": tutorial["like_count"]}

@router.post("/tutorials/{tutorial_id}/bookmark")
async def bookmark_tutorial(
    tutorial_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Bookmark a tutorial."""
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Add to user's bookmarks (would be stored in user profile)
    return {"success": True, "message": "Tutorial bookmarked"}

@router.post("/tutorials/{tutorial_id}/complete")
async def mark_tutorial_complete(
    tutorial_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Mark tutorial as completed by user."""
    tutorial = content_service.get_content("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Update user's tutorial progress
    if not current_user.tutorial_progress:
        current_user.tutorial_progress = {}
    
    current_user.tutorial_progress[tutorial_id] = {
        "completed": True,
        "completed_at": datetime.utcnow().isoformat(),
        "rating": None
    }
    
    # Update tutorial completion rate
    # In production, this would aggregate all user completions
    tutorial["completion_rate"] = min(tutorial.get("completion_rate", 0) + 0.1, 1.0)
    content_service.update_content("tutorials", tutorial_id, {"completion_rate": tutorial["completion_rate"]})
    
    return {"success": True, "message": "Tutorial marked as completed"}

# Initialize sample content on startup
@router.on_event("startup")
async def initialize_sample_content():
    """Initialize sample content if none exists."""
    try:
        stats = content_service.get_content_stats()
        if stats["total_content"] == 0:
            content_service.initialize_sample_content()
    except Exception as e:
        print(f"Error initializing sample content: {e}")