"""Content management service for Baobab AI Labs tutorials, guides, and resources."""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib
import re

class ContentService:
    def __init__(self, content_dir: str = "content"):
        self.content_dir = Path(content_dir)
        self.content_dir.mkdir(exist_ok=True)
        self._init_directories()
        
    def _init_directories(self):
        """Initialize content directory structure."""
        subdirs = [
            "tutorials", "guides", "case_studies", 
            "tool_reviews", "blog_posts", "videos"
        ]
        for subdir in subdirs:
            (self.content_dir / subdir).mkdir(exist_ok=True)
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_id(self, title: str, author_id: str) -> str:
        """Generate unique content ID."""
        content = f"{title}_{author_id}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_content_path(self, content_type: str, content_id: str) -> Path:
        """Get file path for content."""
        return self.content_dir / content_type / f"{content_id}.json"
    
    def create_tutorial(self, tutorial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tutorial."""
        content_id = self._generate_id(tutorial_data["title"], tutorial_data["author_id"])
        slug = self._generate_slug(tutorial_data["title"])
        
        tutorial = {
            "id": content_id,
            "slug": slug,
            "content_type": "tutorial",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "draft",
            "view_count": 0,
            "like_count": 0,
            "completion_rate": 0.0,
            **tutorial_data
        }
        
        # Add default African context if not specified
        if not tutorial.get("african_countries"):
            tutorial["african_countries"] = ["general"]
        if not tutorial.get("languages"):
            tutorial["languages"] = ["en"]
        
        # Save to file
        file_path = self._get_content_path("tutorials", content_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tutorial, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Created tutorial: {content_id} - {tutorial['title']}")
        return tutorial
    
    def create_case_study(self, case_study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new case study."""
        content_id = self._generate_id(case_study_data["title"], case_study_data["author_id"])
        
        case_study = {
            "id": content_id,
            "content_type": "case_study",
            "created_at": datetime.utcnow().isoformat(),
            "status": "draft",
            "view_count": 0,
            "like_count": 0,
            "share_count": 0,
            **case_study_data
        }
        
        # Save to file
        file_path = self._get_content_path("case_studies", content_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(case_study, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Created case study: {content_id} - {case_study['title']}")
        return case_study
    
    def create_tool_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool review."""
        content_id = self._generate_id(review_data["tool_name"], review_data["author_id"])
        
        review = {
            "id": content_id,
            "content_type": "tool_review",
            "reviewed_date": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "status": "draft",
            **review_data
        }
        
        # Save to file
        file_path = self._get_content_path("tool_reviews", content_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(review, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Created tool review: {content_id} - {review['tool_name']}")
        return review
    
    def get_content(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        file_path = self._get_content_path(content_type, content_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Increment view count
            content["view_count"] = content.get("view_count", 0) + 1
            self._save_content(content_type, content_id, content)
            
            return content
        except Exception as e:
            logging.error(f"Error loading content {content_id}: {e}")
            return None
    
    def _save_content(self, content_type: str, content_id: str, content: Dict[str, Any]):
        """Save content to file."""
        file_path = self._get_content_path(content_type, content_id)
        content["updated_at"] = datetime.utcnow().isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    
    def update_content(self, content_type: str, content_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing content."""
        content = self.get_content(content_type, content_id)
        if not content:
            return None
        
        # Don't count view from update operation
        content["view_count"] -= 1
        
        # Apply updates
        for key, value in updates.items():
            if key not in ["id", "created_at", "content_type"]:
                content[key] = value
        
        self._save_content(content_type, content_id, content)
        logging.info(f"Updated {content_type}: {content_id}")
        return content
    
    def delete_content(self, content_type: str, content_id: str) -> bool:
        """Delete content."""
        file_path = self._get_content_path(content_type, content_id)
        if file_path.exists():
            file_path.unlink()
            logging.info(f"Deleted {content_type}: {content_id}")
            return True
        return False
    
    def list_content(self, 
                    content_type: str,
                    status: Optional[str] = None,
                    author_id: Optional[str] = None,
                    country: Optional[str] = None,
                    language: Optional[str] = None,
                    limit: int = 20,
                    offset: int = 0) -> List[Dict[str, Any]]:
        """List content with filters."""
        content_dir = self.content_dir / content_type
        if not content_dir.exists():
            return []
        
        content_list = []
        for file_path in content_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                # Apply filters
                if status and content.get("status") != status:
                    continue
                if author_id and content.get("author_id") != author_id:
                    continue
                if country and country not in content.get("african_countries", []):
                    continue
                if language and language not in content.get("languages", ["en"]):
                    continue
                
                content_list.append(content)
            except Exception as e:
                logging.error(f"Error loading {file_path}: {e}")
        
        # Sort by created_at descending
        content_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        return content_list[offset:offset + limit]
    
    def search_content(self, 
                      query: str,
                      content_types: List[str] = None,
                      countries: List[str] = None,
                      limit: int = 20) -> List[Dict[str, Any]]:
        """Search content by text query."""
        if not content_types:
            content_types = ["tutorials", "guides", "case_studies", "tool_reviews"]
        
        results = []
        query_lower = query.lower()
        
        for content_type in content_types:
            content_list = self.list_content(content_type, limit=1000)  # Get all for search
            
            for content in content_list:
                # Search in title, description, content body, tags
                searchable_text = " ".join([
                    content.get("title", ""),
                    content.get("description", ""),
                    content.get("content_body", ""),
                    " ".join(content.get("tags", [])),
                    " ".join(content.get("categories", []))
                ]).lower()
                
                if query_lower in searchable_text:
                    # Add relevance score (simple implementation)
                    title_match = query_lower in content.get("title", "").lower()
                    content["relevance_score"] = 2 if title_match else 1
                    
                    # Filter by countries if specified
                    if countries:
                        content_countries = content.get("african_countries", [])
                        if not any(country in content_countries for country in countries):
                            continue
                    
                    results.append(content)
        
        # Sort by relevance and date
        results.sort(key=lambda x: (x.get("relevance_score", 0), x.get("created_at", "")), reverse=True)
        return results[:limit]
    
    def get_featured_content(self, content_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured content."""
        if content_type:
            content_types = [content_type]
        else:
            content_types = ["tutorials", "guides", "case_studies", "tool_reviews"]
        
        featured = []
        for ctype in content_types:
            content_list = self.list_content(ctype, status="published", limit=100)
            
            # Sort by engagement metrics
            for content in content_list:
                engagement_score = (
                    content.get("view_count", 0) * 1 +
                    content.get("like_count", 0) * 5 +
                    content.get("completion_rate", 0) * 10
                )
                content["engagement_score"] = engagement_score
            
            content_list.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
            featured.extend(content_list[:limit//len(content_types)])
        
        return featured[:limit]
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get content statistics."""
        stats = {
            "total_content": 0,
            "content_by_type": {},
            "content_by_difficulty": {},
            "content_by_country": {},
            "most_viewed": [],
            "recent_content": []
        }
        
        content_types = ["tutorials", "guides", "case_studies", "tool_reviews"]
        all_content = []
        
        for content_type in content_types:
            content_list = self.list_content(content_type, limit=1000)
            stats["content_by_type"][content_type] = len(content_list)
            stats["total_content"] += len(content_list)
            all_content.extend(content_list)
            
            # Difficulty stats
            for content in content_list:
                difficulty = content.get("difficulty_level", "unknown")
                stats["content_by_difficulty"][difficulty] = stats["content_by_difficulty"].get(difficulty, 0) + 1
                
                # Country stats
                for country in content.get("african_countries", ["unknown"]):
                    stats["content_by_country"][country] = stats["content_by_country"].get(country, 0) + 1
        
        # Most viewed content
        all_content.sort(key=lambda x: x.get("view_count", 0), reverse=True)
        stats["most_viewed"] = all_content[:10]
        
        # Recent content
        all_content.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        stats["recent_content"] = all_content[:10]
        
        return stats
    
    def initialize_sample_content(self):
        """Initialize with sample African AI content."""
        sample_tutorials = [
            {
                "title": "Building AI-Powered Customer Service for African SMEs",
                "description": "Learn to implement chatbots that understand local languages and cultural context",
                "author_id": "admin",
                "author_name": "Baobab AI Team",
                "difficulty_level": "intermediate",
                "content_body": """# Building AI-Powered Customer Service for African SMEs

## Introduction
Small and medium enterprises (SMEs) across Africa are increasingly looking to AI to improve customer service while managing costs effectively.

## What You'll Learn
- Set up multilingual chatbots supporting English, French, Swahili
- Integrate with popular African messaging platforms (WhatsApp, SMS)
- Handle cultural nuances in customer interactions
- Deploy cost-effectively using cloud services

## Prerequisites
- Basic Python knowledge
- Understanding of REST APIs
- Access to cloud services (AWS, Google Cloud)

## Implementation Steps

### Step 1: Choose Your Platform
For African markets, prioritize:
- WhatsApp Business API (highest penetration)
- SMS integration (universal reach)
- Web chat as secondary option

### Step 2: Language Support
```python
# Example: Multi-language detection
from langdetect import detect

def detect_customer_language(message):
    try:
        lang = detect(message)
        supported_langs = ['en', 'fr', 'sw', 'ha']  # English, French, Swahili, Hausa
        return lang if lang in supported_langs else 'en'
    except:
        return 'en'  # Default to English
```

### Step 3: Cultural Context
Consider local business hours, greeting customs, and payment preferences in your responses.

## Deployment on African Cloud Infrastructure
Use local data centers when available for better latency and compliance with data sovereignty laws.

## Cost Optimization
- Start with rule-based responses for common queries
- Use AI only for complex interactions
- Implement smart routing to human agents

## Success Metrics
- Response time < 30 seconds
- Resolution rate > 70%
- Customer satisfaction > 4.0/5.0

## Case Studies
Several Nigerian and Kenyan SMEs have achieved 40% reduction in customer service costs using this approach.
""",
                "tags": ["chatbot", "customer-service", "sme", "whatsapp"],
                "categories": ["business-ai", "nlp"],
                "african_countries": ["nigeria", "kenya", "south_africa", "general"],
                "languages": ["en", "fr"],
                "estimated_duration": 120,
                "prerequisites": ["python-basics", "api-knowledge"],
                "learning_objectives": [
                    "Implement multilingual customer service bots",
                    "Integrate with African messaging platforms",
                    "Deploy cost-effectively in African markets"
                ]
            },
            {
                "title": "Machine Learning pour l'Agriculture en Afrique de l'Ouest",
                "description": "Utilisez l'IA pour optimiser les rendements agricoles en tenant compte du climat africain",
                "author_id": "admin",
                "author_name": "Équipe Baobab AI",
                "difficulty_level": "advanced",
                "content_body": """# Machine Learning pour l'Agriculture en Afrique de l'Ouest

## Introduction
L'agriculture représente 60% de l'emploi en Afrique de l'Ouest. L'IA peut transformer ce secteur.

## Objectifs d'Apprentissage
- Analyser les données climatiques africaines
- Prédire les rendements des cultures locales
- Optimiser l'utilisation de l'eau
- Détecter les maladies des cultures par vision artificielle

## Données Spécifiques à l'Afrique
- Patterns de précipitations irréguliers
- Variabilité des sols
- Cultures locales (mil, sorgho, igname)
- Contraintes infrastructurelles

## Code Exemple : Prédiction des Rendements
```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Données climatiques ouest-africaines
def prepare_west_africa_data():
    # Température, précipitations, humidité du sol
    # Données satellites disponibles via Google Earth Engine
    pass

def predict_crop_yield(crop_type, location, season_data):
    # Modèle spécialisé pour les conditions ouest-africaines
    model = RandomForestRegressor(n_estimators=100)
    # ... implementation
    return predicted_yield
```

## Intégration Mobile
Développez des applications SMS/USSD pour les agriculteurs sans smartphones.

## Impact Attendu
- Augmentation des rendements de 15-25%
- Réduction du gaspillage d'eau de 30%
- Détection précoce des maladies
""",
                "tags": ["agriculture", "machine-learning", "climat"],
                "categories": ["agriculture-ai", "data-science"],
                "african_countries": ["senegal", "mali", "burkina_faso", "niger"],
                "languages": ["fr"],
                "estimated_duration": 180
            }
        ]
        
        sample_case_studies = [
            {
                "title": "Flutterwave: AI-Powered Fraud Detection for African Payments",
                "company_name": "Flutterwave",
                "country": "nigeria",
                "industry": "fintech",
                "challenge": "High fraud rates in cross-border African payments were causing significant losses and reducing customer trust.",
                "solution": "Implemented machine learning models to detect fraudulent transactions in real-time, considering African payment patterns and behaviors.",
                "implementation": "Built ensemble models using XGBoost and neural networks, integrated with their payment infrastructure, trained on 2+ years of African transaction data.",
                "results": "Reduced fraud by 85%, saved $50M+ annually, improved customer trust, enabled expansion to 15+ African countries.",
                "author_id": "admin",
                "technologies_used": ["python", "xgboost", "tensorflow", "kafka", "redis"],
                "roi_percentage": 300.0,
                "time_saved": "Real-time fraud detection vs 24-48 hour manual review",
                "team_size": 12,
                "implementation_duration": "8 months"
            }
        ]
        
        # Create sample content
        for tutorial in sample_tutorials:
            self.create_tutorial(tutorial)
        
        for case_study in sample_case_studies:
            self.create_case_study(case_study)
        
        logging.info("Sample content initialized successfully")