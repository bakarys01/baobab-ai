from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional

class Question(BaseModel):
    question: str = Field(..., description="User question")
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chat history")

    @validator("history", pre=True, always=True)
    def validate_history(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("history must be a list of dicts")
        for item in v:
            if not isinstance(item, dict) or "role" not in item or "message" not in item:
                raise ValueError("Each history item must be a dict with 'role' and 'message'")
        return v

class Answer(BaseModel):
    answer: str = Field(..., description="Model answer")

__all__ = ["Question", "Answer"]