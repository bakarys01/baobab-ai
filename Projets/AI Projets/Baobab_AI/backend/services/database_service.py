"""Database service layer for Baobab AI."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from models.database_models import User, ChatSession, Tutorial, TutorialProgress, CaseStudy, CommunityPost, Comment, KnowledgeBase
from database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

class UserService:
    """Service for user management."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, **kwargs) -> User:
        """Create a new user."""
        hashed_password = UserService.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Username or email already exists")
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Update user information."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

class ChatService:
    """Service for chat session management."""
    
    @staticmethod
    def create_chat_session(db: Session, user_id: int, title: str = None) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            user_id=user_id,
            title=title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            messages=[]
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_user_chat_sessions(db: Session, user_id: int) -> List[ChatSession]:
        """Get all chat sessions for a user."""
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
    
    @staticmethod
    def get_chat_session(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a specific chat session."""
        return db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
    
    @staticmethod
    def add_message_to_session(db: Session, session_id: int, user_id: int, role: str, message: str) -> Optional[ChatSession]:
        """Add a message to a chat session."""
        session = ChatService.get_chat_session(db, session_id, user_id)
        if not session:
            return None
        
        if not session.messages:
            session.messages = []
        
        session.messages.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        db.commit()
        db.refresh(session)
        return session

class ContentService:
    """Service for content management (tutorials, case studies)."""
    
    @staticmethod
    def get_tutorials(db: Session, category: str = None, difficulty: str = None) -> List[Tutorial]:
        """Get published tutorials with optional filtering."""
        query = db.query(Tutorial).filter(Tutorial.is_published == True)
        
        if category:
            query = query.filter(Tutorial.category == category)
        if difficulty:
            query = query.filter(Tutorial.difficulty == difficulty)
        
        return query.order_by(Tutorial.created_at.desc()).all()
    
    @staticmethod
    def get_tutorial_by_id(db: Session, tutorial_id: int) -> Optional[Tutorial]:
        """Get a specific tutorial."""
        return db.query(Tutorial).filter(
            Tutorial.id == tutorial_id,
            Tutorial.is_published == True
        ).first()
    
    @staticmethod
    def create_tutorial(db: Session, **kwargs) -> Tutorial:
        """Create a new tutorial."""
        tutorial = Tutorial(**kwargs)
        db.add(tutorial)
        db.commit()
        db.refresh(tutorial)
        return tutorial
    
    @staticmethod
    def get_case_studies(db: Session, country: str = None, industry: str = None) -> List[CaseStudy]:
        """Get published case studies with optional filtering."""
        query = db.query(CaseStudy).filter(CaseStudy.is_published == True)
        
        if country:
            query = query.filter(CaseStudy.country == country)
        if industry:
            query = query.filter(CaseStudy.industry == industry)
        
        return query.order_by(CaseStudy.created_at.desc()).all()
    
    @staticmethod
    def get_case_study_by_id(db: Session, case_study_id: int) -> Optional[CaseStudy]:
        """Get a specific case study."""
        return db.query(CaseStudy).filter(
            CaseStudy.id == case_study_id,
            CaseStudy.is_published == True
        ).first()
    
    @staticmethod
    def track_tutorial_progress(db: Session, user_id: int, tutorial_id: int, progress_percentage: int) -> TutorialProgress:
        """Track or update tutorial progress for a user."""
        progress = db.query(TutorialProgress).filter(
            TutorialProgress.user_id == user_id,
            TutorialProgress.tutorial_id == tutorial_id
        ).first()
        
        if progress:
            progress.progress_percentage = progress_percentage
            progress.completed = progress_percentage >= 100
            progress.last_accessed = datetime.now()
        else:
            progress = TutorialProgress(
                user_id=user_id,
                tutorial_id=tutorial_id,
                progress_percentage=progress_percentage,
                completed=progress_percentage >= 100,
                last_accessed=datetime.now()
            )
            db.add(progress)
        
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def get_user_tutorial_progress(db: Session, user_id: int) -> List[TutorialProgress]:
        """Get all tutorial progress for a user."""
        return db.query(TutorialProgress).filter(TutorialProgress.user_id == user_id).all()

class CommunityService:
    """Service for community features."""
    
    @staticmethod
    def get_posts(db: Session, category: str = None, limit: int = 20, offset: int = 0) -> List[CommunityPost]:
        """Get published community posts."""
        query = db.query(CommunityPost).filter(CommunityPost.is_published == True)
        
        if category:
            query = query.filter(CommunityPost.category == category)
        
        return query.order_by(CommunityPost.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> Optional[CommunityPost]:
        """Get a specific community post."""
        return db.query(CommunityPost).filter(
            CommunityPost.id == post_id,
            CommunityPost.is_published == True
        ).first()
    
    @staticmethod
    def create_post(db: Session, title: str, content: str, author_id: int, **kwargs) -> CommunityPost:
        """Create a new community post."""
        post = CommunityPost(
            title=title,
            content=content,
            author_id=author_id,
            **kwargs
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def get_post_comments(db: Session, post_id: int) -> List[Comment]:
        """Get comments for a post."""
        return db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.is_published == True
        ).order_by(Comment.created_at.asc()).all()
    
    @staticmethod
    def create_comment(db: Session, content: str, author_id: int, post_id: int, parent_id: int = None) -> Comment:
        """Create a new comment."""
        comment = Comment(
            content=content,
            author_id=author_id,
            post_id=post_id,
            parent_id=parent_id
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

class KnowledgeBaseService:
    """Service for knowledge base management."""
    
    @staticmethod
    def get_knowledge_entries(db: Session, category: str = None, language: str = None) -> List[KnowledgeBase]:
        """Get active knowledge base entries."""
        query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
        
        if category:
            query = query.filter(KnowledgeBase.category == category)
        if language:
            query = query.filter(KnowledgeBase.language == language)
        
        return query.all()
    
    @staticmethod
    def add_knowledge_entry(db: Session, title: str, content: str, **kwargs) -> KnowledgeBase:
        """Add a new knowledge base entry."""
        entry = KnowledgeBase(
            title=title,
            content=content,
            **kwargs
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def search_knowledge_base(db: Session, query_text: str, limit: int = 10) -> List[KnowledgeBase]:
        """Search knowledge base entries by text."""
        return db.query(KnowledgeBase).filter(
            KnowledgeBase.is_active == True,
            KnowledgeBase.content.contains(query_text)
        ).limit(limit).all()