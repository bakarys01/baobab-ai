"""Community models for Baobab AI Labs forums, discussions, and interactions."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PostType(str, Enum):
    DISCUSSION = "discussion"
    QUESTION = "question"
    SUCCESS_STORY = "success_story"
    ANNOUNCEMENT = "announcement"
    RESOURCE_SHARE = "resource_share"

class PostStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PINNED = "pinned"
    ARCHIVED = "archived"

class ReactionType(str, Enum):
    LIKE = "like"
    HELPFUL = "helpful"
    INSIGHTFUL = "insightful"
    CELEBRATE = "celebrate"

class ForumCategory(str, Enum):
    GENERAL = "general"
    TUTORIALS = "tutorials"
    SUCCESS_STORIES = "success_stories"
    HELP_SUPPORT = "help_support"
    TOOLS_RESOURCES = "tools_resources"
    COUNTRY_SPECIFIC = "country_specific"
    JOBS_OPPORTUNITIES = "jobs_opportunities"
    EVENTS_MEETUPS = "events_meetups"

class CommunityPost(BaseModel):
    id: Optional[str] = Field(None, description="Post ID")
    title: str = Field(..., max_length=200, description="Post title")
    content: str = Field(..., description="Post content (markdown)")
    post_type: PostType = Field(..., description="Type of post")
    category: ForumCategory = Field(..., description="Forum category")
    
    # Author info
    author_id: str = Field(..., description="Author user ID")
    author_name: str = Field(..., description="Author display name")
    author_country: Optional[str] = Field(None, description="Author's country")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Post tags")
    mentioned_users: List[str] = Field(default_factory=list, description="Mentioned user IDs")
    
    # Status and timestamps
    status: PostStatus = Field(PostStatus.ACTIVE, description="Post status")
    is_answered: bool = Field(False, description="Question has been answered")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Engagement metrics
    view_count: int = Field(0, description="Number of views")
    reply_count: int = Field(0, description="Number of replies")
    reaction_count: int = Field(0, description="Total reactions")
    reactions: Dict[str, int] = Field(default_factory=dict, description="Reaction counts by type")
    
    # Moderation
    is_featured: bool = Field(False, description="Featured post")
    report_count: int = Field(0, description="Number of reports")
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Too many tags')
        return [tag.lower().strip() for tag in v if tag.strip()]

class PostCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., min_length=10)
    post_type: PostType
    category: ForumCategory
    tags: List[str] = Field(default_factory=list)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None
    status: Optional[PostStatus] = None

class Comment(BaseModel):
    id: Optional[str] = Field(None, description="Comment ID")
    post_id: str = Field(..., description="Parent post ID")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    
    # Content
    content: str = Field(..., description="Comment content (markdown)")
    
    # Author info
    author_id: str = Field(..., description="Author user ID")
    author_name: str = Field(..., description="Author display name")
    author_country: Optional[str] = Field(None, description="Author's country")
    
    # Status
    is_answer: bool = Field(False, description="Marked as answer to question")
    is_pinned: bool = Field(False, description="Pinned comment")
    is_edited: bool = Field(False, description="Comment has been edited")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Engagement
    reaction_count: int = Field(0, description="Total reactions")
    reactions: Dict[str, int] = Field(default_factory=dict, description="Reaction counts by type")
    reply_count: int = Field(0, description="Number of direct replies")
    
    # Moderation
    report_count: int = Field(0, description="Number of reports")

class CommentCreate(BaseModel):
    post_id: str
    content: str = Field(..., min_length=3)
    parent_comment_id: Optional[str] = None

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=3)

class Reaction(BaseModel):
    id: Optional[str] = None
    user_id: str = Field(..., description="User who reacted")
    target_type: str = Field(..., description="Type of target (post/comment)")
    target_id: str = Field(..., description="ID of target")
    reaction_type: ReactionType = Field(..., description="Type of reaction")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserFollow(BaseModel):
    id: Optional[str] = None
    follower_id: str = Field(..., description="User who follows")
    following_id: str = Field(..., description="User being followed")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str = Field(..., description="User to notify")
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., max_length=500, description="Notification message")
    notification_type: str = Field(..., description="Type of notification")
    
    # Related objects
    related_post_id: Optional[str] = None
    related_comment_id: Optional[str] = None
    related_user_id: Optional[str] = None
    
    # Status
    is_read: bool = Field(False, description="Notification read status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

class SuccessStory(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., max_length=200, description="Success story title")
    summary: str = Field(..., max_length=300, description="Brief summary")
    full_story: str = Field(..., description="Complete success story")
    
    # Company/individual info
    company_name: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., description="African country")
    city: Optional[str] = Field(None, max_length=100)
    
    # Impact metrics
    impact_metrics: Dict[str, Any] = Field(default_factory=dict, description="Impact measurements")
    roi_achieved: Optional[str] = Field(None, description="ROI description")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    
    # Technical details
    ai_technologies: List[str] = Field(default_factory=list, description="AI technologies used")
    challenges_overcome: List[str] = Field(default_factory=list, description="Challenges faced")
    lessons_learned: List[str] = Field(default_factory=list, description="Key lessons")
    
    # Media
    images: List[str] = Field(default_factory=list, description="Image URLs")
    video_url: Optional[str] = Field(None, description="Video URL")
    
    # Author and validation
    author_id: str = Field(..., description="Story author")
    is_verified: bool = Field(False, description="Story has been verified")
    verified_by: Optional[str] = Field(None, description="Verified by user ID")
    
    # Publishing
    status: str = Field("pending", description="Approval status")
    featured: bool = Field(False, description="Featured success story")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Engagement
    view_count: int = Field(0)
    like_count: int = Field(0)
    share_count: int = Field(0)

class Event(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., max_length=200)
    description: str = Field(..., description="Event description")
    event_type: str = Field(..., description="Type of event (webinar, meetup, conference)")
    
    # Scheduling
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    timezone: str = Field(..., description="Event timezone")
    
    # Location
    is_online: bool = Field(True, description="Online event")
    venue_name: Optional[str] = Field(None, max_length=200)
    venue_address: Optional[str] = Field(None, max_length=300)
    country: str = Field(..., description="Event country")
    city: Optional[str] = Field(None, max_length=100)
    
    # Links
    registration_url: Optional[str] = Field(None, description="Registration URL")
    meeting_url: Optional[str] = Field(None, description="Meeting URL")
    recording_url: Optional[str] = Field(None, description="Recording URL")
    
    # Organizer
    organizer_id: str = Field(..., description="Event organizer user ID")
    organizer_name: str = Field(..., description="Organizer display name")
    
    # Capacity and registration
    max_attendees: Optional[int] = Field(None, description="Maximum attendees")
    registered_count: int = Field(0, description="Number of registered attendees")
    
    # Content
    topics: List[str] = Field(default_factory=list, description="Event topics")
    speakers: List[Dict[str, str]] = Field(default_factory=list, description="Speaker information")
    
    # Status
    status: str = Field("upcoming", description="Event status")
    is_featured: bool = Field(False, description="Featured event")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityStats(BaseModel):
    total_posts: int
    total_comments: int
    total_users: int
    active_users_today: int
    posts_by_category: Dict[str, int]
    posts_by_country: Dict[str, int]
    top_contributors: List[Dict[str, Any]]
    trending_topics: List[str]
    recent_success_stories: List[Dict[str, Any]]