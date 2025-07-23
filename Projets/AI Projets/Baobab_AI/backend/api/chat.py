"""Enhanced chat API with African context and multi-language support."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from models.user import UserProfile
from services.rag_service import AfricanRAGService
from api.auth import get_current_user
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
rag_service = AfricanRAGService()

class ChatMessage(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    language: str = Field("en", description="Response language (en, fr, sw, ha)")
    context_preference: str = Field("african", description="Context preference (african, global)")
    history: Optional[List[Dict]] = Field(default_factory=list, description="Chat history")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI response")
    language: str = Field(..., description="Response language")
    sources_used: List[str] = Field(default_factory=list, description="Information sources")
    african_context: bool = Field(True, description="Used African context")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class ChatSettings(BaseModel):
    preferred_language: str = Field("en", description="Default language")
    include_web_search: bool = Field(True, description="Include web search results")
    african_focus: bool = Field(True, description="Prioritize African sources")
    max_sources: int = Field(5, ge=1, le=10, description="Maximum web sources")

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    message: ChatMessage,
    current_user: Optional[UserProfile] = Depends(get_current_user)
):
    """Ask a question to the AI assistant with African context."""
    try:
        import time
        start_time = time.time()
        
        # Use user's preferred language if not specified
        language = message.language
        if current_user and not language:
            language = current_user.preferred_language
        
        # Determine if we should use African focus
        african_focus = message.context_preference == "african"
        if current_user and current_user.country:
            african_focus = True
        
        # Generate response using enhanced RAG service
        response = rag_service.run_enhanced_rag(
            question=message.question,
            language=language,
            num_web_sources=5,
            include_african_context=True,
            search_african_focus=african_focus
        )
        
        processing_time = time.time() - start_time
        
        # Extract sources from response (if any)
        sources = []
        if "Sources :" in response or "📚 Sources" in response:
            sources_section = response.split("📚 Sources")[-1] if "📚 Sources" in response else response.split("Sources :")[-1]
            # Simple extraction - in production, this would be more sophisticated
            sources = [line.strip("• -") for line in sources_section.split("\n") if line.strip() and ("http" in line or "www" in line)]
        
        return ChatResponse(
            answer=response,
            language=language,
            sources_used=sources[:3],  # Limit to top 3 sources
            african_context=african_focus,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.post("/ask-anonymous", response_model=ChatResponse)
async def ask_question_anonymous(message: ChatMessage):
    """Ask a question without authentication (limited features)."""
    try:
        import time
        start_time = time.time()
        
        # Default to African context for anonymous users
        response = rag_service.run_enhanced_rag(
            question=message.question,
            language=message.language,
            num_web_sources=3,  # Reduced for anonymous users
            include_african_context=True,
            search_african_focus=True
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            answer=response,
            language=message.language,
            sources_used=[],  # No sources for anonymous users
            african_context=True,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logging.error(f"Anonymous chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing question")

@router.get("/settings", response_model=ChatSettings)
async def get_chat_settings(current_user: UserProfile = Depends(get_current_user)):
    """Get user's chat settings."""
    return ChatSettings(
        preferred_language=current_user.preferred_language,
        include_web_search=True,
        african_focus=True,
        max_sources=5
    )

@router.put("/settings", response_model=ChatSettings)
async def update_chat_settings(
    settings: ChatSettings,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update user's chat settings."""
    # In production, this would save to user profile
    return settings

@router.get("/languages", response_model=List[Dict[str, str]])
async def get_supported_languages():
    """Get list of supported languages."""
    return [
        {"code": "en", "name": "English", "native_name": "English"},
        {"code": "fr", "name": "French", "native_name": "Français"},
        {"code": "sw", "name": "Swahili", "native_name": "Kiswahili"},
        {"code": "ha", "name": "Hausa", "native_name": "Hausa"},
        {"code": "ar", "name": "Arabic", "native_name": "العربية"},
        {"code": "pt", "name": "Portuguese", "native_name": "Português"}
    ]

@router.get("/context-info", response_model=Dict[str, str])
async def get_context_info():
    """Get information about the AI's knowledge context."""
    return {
        "african_knowledge": "Specialized knowledge about African AI market, startups, languages, and business contexts",
        "web_search": "Real-time web search for current information and African sources",
        "languages": "Multi-language support with cultural context awareness",
        "business_focus": "Emphasis on practical implementation for African businesses and SMEs",
        "data_sources": "Combination of curated African AI content and live web sources"
    }

@router.post("/feedback")
async def submit_chat_feedback(
    feedback_data: Dict[str, str],
    current_user: Optional[UserProfile] = Depends(get_current_user)
):
    """Submit feedback about chat responses."""
    # In production, this would store feedback for model improvement
    return {"success": True, "message": "Feedback submitted successfully"}

# Health check endpoint
@router.get("/health")
async def chat_health():
    """Check chat service health."""
    try:
        # Test RAG service
        test_response = rag_service.run_enhanced_rag(
            question="What is AI?",
            language="en",
            num_web_sources=1,
            include_african_context=False,
            search_african_focus=False
        )
        
        return {
            "status": "healthy",
            "rag_service": "operational",
            "test_response_length": len(test_response)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }