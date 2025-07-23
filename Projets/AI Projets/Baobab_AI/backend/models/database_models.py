"""SQLAlchemy database models for Baobab AI."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    country = Column(String(50))
    profession = Column(String(100))
    experience_level = Column(String(20))  # beginner, intermediate, advanced
    interests = Column(JSON)  # List of interests
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")
    tutorial_progress = relationship("TutorialProgress", back_populates="user")
    community_posts = relationship("CommunityPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class ChatSession(Base):
    """Chat session model to store conversation history."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    messages = Column(JSON)  # Store chat messages as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")

class Tutorial(Base):
    """Tutorial content model."""
    __tablename__ = "tutorials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # business, tech, marketing, etc.
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    duration_minutes = Column(Integer)
    tags = Column(JSON)  # List of tags
    author = Column(String(100))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    progress_records = relationship("TutorialProgress", back_populates="tutorial")

class TutorialProgress(Base):
    """Track user progress in tutorials."""
    __tablename__ = "tutorial_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tutorial_id = Column(Integer, ForeignKey("tutorials.id"), nullable=False)
    progress_percentage = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    last_accessed = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="tutorial_progress")
    tutorial = relationship("Tutorial", back_populates="progress_records")

class CaseStudy(Base):
    """African business case studies."""
    __tablename__ = "case_studies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company_name = Column(String(100))
    country = Column(String(50))
    industry = Column(String(50))
    description = Column(Text)
    content = Column(Text, nullable=False)
    key_insights = Column(JSON)  # List of key insights
    tags = Column(JSON)
    author = Column(String(100))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CommunityPost(Base):
    """Community forum posts."""
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50))
    tags = Column(JSON)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="community_posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    """Comments on community posts."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # For nested comments
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("CommunityPost", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])

class KnowledgeBase(Base):
    """Knowledge base entries for RAG system."""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    source = Column(String(200))  # URL or document source
    category = Column(String(50))
    language = Column(String(10))  # en, fr, sw, etc.
    tags = Column(JSON)
    embedding_vector = Column(JSON)  # Store FAISS embeddings as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())