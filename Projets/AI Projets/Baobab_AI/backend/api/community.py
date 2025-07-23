"""Community API endpoints for forums, discussions, and success stories."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.community import (
    CommunityPost, PostCreate, PostUpdate, Comment, CommentCreate, CommentUpdate,
    SuccessStory, Event, PostType, ForumCategory, PostStatus
)
from models.user import UserProfile
from services.content_service import ContentService
from api.auth import get_current_user
import json
from pathlib import Path

router = APIRouter(prefix="/community", tags=["community"])

# Simple file-based storage for community content
COMMUNITY_DIR = Path("community")
COMMUNITY_DIR.mkdir(exist_ok=True)
(COMMUNITY_DIR / "posts").mkdir(exist_ok=True)
(COMMUNITY_DIR / "comments").mkdir(exist_ok=True)
(COMMUNITY_DIR / "success_stories").mkdir(exist_ok=True)
(COMMUNITY_DIR / "events").mkdir(exist_ok=True)

class CommunityService:
    @staticmethod
    def save_post(post: dict) -> bool:
        """Save community post to file."""
        try:
            file_path = COMMUNITY_DIR / "posts" / f"{post['id']}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(post, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving post: {e}")
            return False
    
    @staticmethod
    def get_post(post_id: str) -> Optional[dict]:
        """Get post by ID."""
        try:
            file_path = COMMUNITY_DIR / "posts" / f"{post_id}.json"
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    @staticmethod
    def list_posts(category: Optional[str] = None, 
                  post_type: Optional[str] = None,
                  author_id: Optional[str] = None,
                  limit: int = 20,
                  offset: int = 0) -> List[dict]:
        """List posts with filters."""
        posts = []
        for file_path in (COMMUNITY_DIR / "posts").glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = json.load(f)
                
                # Apply filters
                if category and post.get("category") != category:
                    continue
                if post_type and post.get("post_type") != post_type:
                    continue
                if author_id and post.get("author_id") != author_id:
                    continue
                
                posts.append(post)
            except Exception:
                continue
        
        # Sort by created_at descending
        posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return posts[offset:offset + limit]
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        import hashlib
        content = f"{datetime.utcnow().isoformat()}_{hash(datetime.utcnow())}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

community_service = CommunityService()

# Forum Posts Endpoints
@router.post("/posts", response_model=dict)
async def create_post(
    post_data: PostCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new community post."""
    post_id = community_service.generate_id()
    
    post = {
        "id": post_id,
        "title": post_data.title,
        "content": post_data.content,
        "post_type": post_data.post_type,
        "category": post_data.category,
        "tags": post_data.tags,
        "author_id": current_user.id,
        "author_name": current_user.full_name,
        "author_country": current_user.country,
        "mentioned_users": [],
        "status": "active",
        "is_answered": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
        "closed_at": None,
        "view_count": 0,
        "reply_count": 0,
        "reaction_count": 0,
        "reactions": {},
        "is_featured": False,
        "report_count": 0
    }
    
    if not community_service.save_post(post):
        raise HTTPException(status_code=500, detail="Failed to create post")
    
    return {"success": True, "post": post}

@router.get("/posts", response_model=List[dict])
async def list_posts(
    category: Optional[ForumCategory] = Query(None, description="Filter by category"),
    post_type: Optional[PostType] = Query(None, description="Filter by post type"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    featured: Optional[bool] = Query(None, description="Filter featured posts"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List community posts with filters."""
    posts = community_service.list_posts(
        category=category,
        post_type=post_type,
        author_id=author_id,
        limit=limit,
        offset=offset
    )
    
    if featured is not None:
        posts = [p for p in posts if p.get("is_featured", False) == featured]
    
    return posts

@router.get("/posts/{post_id}", response_model=dict)
async def get_post(post_id: str):
    """Get a specific post and increment view count."""
    post = community_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post["view_count"] = post.get("view_count", 0) + 1
    community_service.save_post(post)
    
    return post

@router.put("/posts/{post_id}", response_model=dict)
async def update_post(
    post_id: str,
    post_updates: PostUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a post."""
    post = community_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check authorization
    if post["author_id"] != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Apply updates
    update_data = post_updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        post[key] = value
    
    post["updated_at"] = datetime.utcnow().isoformat()
    
    if not community_service.save_post(post):
        raise HTTPException(status_code=500, detail="Failed to update post")
    
    return {"success": True, "post": post}

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a post."""
    post = community_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check authorization
    if post["author_id"] != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete post file
    file_path = COMMUNITY_DIR / "posts" / f"{post_id}.json"
    if file_path.exists():
        file_path.unlink()
    
    return {"success": True, "message": "Post deleted successfully"}

# Success Stories Endpoints
@router.post("/success-stories", response_model=dict)
async def create_success_story(
    story_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new success story."""
    story_id = community_service.generate_id()
    
    story = {
        "id": story_id,
        "author_id": current_user.id,
        "status": "pending",
        "is_verified": False,
        "verified_by": None,
        "featured": False,
        "created_at": datetime.utcnow().isoformat(),
        "published_at": None,
        "view_count": 0,
        "like_count": 0,
        "share_count": 0,
        **story_data
    }
    
    try:
        file_path = COMMUNITY_DIR / "success_stories" / f"{story_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "story": story}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create success story: {e}")

@router.get("/success-stories", response_model=List[dict])
async def list_success_stories(
    status: Optional[str] = Query("published", description="Filter by status"),
    country: Optional[str] = Query(None, description="Filter by country"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    featured: Optional[bool] = Query(None, description="Filter featured stories"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """List success stories with filters."""
    stories = []
    
    for file_path in (COMMUNITY_DIR / "success_stories").glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                story = json.load(f)
            
            # Apply filters
            if status and story.get("status") != status:
                continue
            if country and story.get("country", "").lower() != country.lower():
                continue
            if industry and story.get("industry", "").lower() != industry.lower():
                continue
            if featured is not None and story.get("featured", False) != featured:
                continue
            
            stories.append(story)
        except Exception:
            continue
    
    # Sort by created_at descending
    stories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return stories[offset:offset + limit]

@router.get("/success-stories/{story_id}", response_model=dict)
async def get_success_story(story_id: str):
    """Get a specific success story."""
    try:
        file_path = COMMUNITY_DIR / "success_stories" / f"{story_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Success story not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            story = json.load(f)
        
        # Increment view count
        story["view_count"] = story.get("view_count", 0) + 1
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        
        return story
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving success story: {e}")

# Reaction Endpoints
@router.post("/posts/{post_id}/react")
async def react_to_post(
    post_id: str,
    reaction_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """React to a post."""
    post = community_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    reaction_type = reaction_data.get("reaction_type", "like")
    
    # Update reaction count
    if "reactions" not in post:
        post["reactions"] = {}
    
    post["reactions"][reaction_type] = post["reactions"].get(reaction_type, 0) + 1
    post["reaction_count"] = sum(post["reactions"].values())
    
    community_service.save_post(post)
    
    return {"success": True, "reactions": post["reactions"]}

# Statistics Endpoints
@router.get("/stats", response_model=dict)
async def get_community_stats():
    """Get community statistics."""
    posts_count = len(list((COMMUNITY_DIR / "posts").glob("*.json")))
    stories_count = len(list((COMMUNITY_DIR / "success_stories").glob("*.json")))
    
    # Analyze posts by category
    posts_by_category = {}
    posts_by_country = {}
    
    for file_path in (COMMUNITY_DIR / "posts").glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = json.load(f)
            
            category = post.get("category", "unknown")
            posts_by_category[category] = posts_by_category.get(category, 0) + 1
            
            country = post.get("author_country", "unknown")
            posts_by_country[country] = posts_by_country.get(country, 0) + 1
        except Exception:
            continue
    
    return {
        "total_posts": posts_count,
        "total_success_stories": stories_count,
        "posts_by_category": posts_by_category,
        "posts_by_country": posts_by_country,
        "active_discussions": posts_count,  # Simplified
    }

@router.get("/trending-topics", response_model=List[str])
async def get_trending_topics():
    """Get trending discussion topics."""
    # Simple implementation - count tag frequency
    tag_counts = {}
    
    for file_path in (COMMUNITY_DIR / "posts").glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = json.load(f)
            
            for tag in post.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        except Exception:
            continue
    
    # Return top 10 trending topics
    trending = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in trending[:10]]

# Initialize sample community content
@router.on_event("startup")
async def initialize_sample_community():
    """Initialize sample community content if none exists."""
    try:
        # Check if we have any posts
        posts = list((COMMUNITY_DIR / "posts").glob("*.json"))
        if len(posts) == 0:
            # Create sample posts
            sample_posts = [
                {
                    "id": "sample_post_1",
                    "title": "Best AI tools for small businesses in Nigeria",
                    "content": "What AI tools have worked well for your small business in Nigeria? Looking for practical solutions that don't break the bank.",
                    "post_type": "question",
                    "category": "tools_resources",
                    "tags": ["sme", "nigeria", "tools", "chatbot"],
                    "author_id": "sample_user",
                    "author_name": "Adaora Okafor",
                    "author_country": "nigeria",
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat(),
                    "view_count": 45,
                    "reply_count": 8,
                    "reactions": {"helpful": 12, "like": 8}
                },
                {
                    "id": "sample_post_2",
                    "title": "Success: Implemented WhatsApp bot for customer service",
                    "content": "Just wanted to share our success story. We implemented a WhatsApp chatbot for our logistics company in Kenya and saw 40% reduction in customer service costs!",
                    "post_type": "success_story",
                    "category": "success_stories",
                    "tags": ["whatsapp", "chatbot", "kenya", "logistics"],
                    "author_id": "sample_user_2",
                    "author_name": "James Kirimi",
                    "author_country": "kenya",
                    "status": "active",
                    "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                    "view_count": 128,
                    "reply_count": 15,
                    "reactions": {"celebrate": 25, "like": 18, "helpful": 12}
                }
            ]
            
            for post in sample_posts:
                community_service.save_post(post)
    except Exception as e:
        print(f"Error initializing sample community content: {e}")