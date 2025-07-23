"""FastAPI entrypoint for Baobab AI backend."""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import des modèles et services
from models import Question, Answer
from llm_pipeline import run_agent

# Import des routes API
from api.auth import router as auth_router
from api.chat import router as chat_router
from api.content import router as content_router
from api.community import router as community_router

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Baobab AI Backend",
    version="2.0.0",
    description="AI-powered RAG chatbot platform designed for African contexts"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes API
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(community_router, prefix="/api/community", tags=["community"])

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "Baobab AI Backend"}

@app.post("/rag", response_model=Answer)
def rag_endpoint(q: Question):
    """Legacy RAG endpoint for backward compatibility."""
    try:
        logger.info(f"RAG query: {q.question[:100]}...")
        answer = run_agent(q.question, history=q.history)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"RAG endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Bienvenue sur Baobab AI Backend",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)