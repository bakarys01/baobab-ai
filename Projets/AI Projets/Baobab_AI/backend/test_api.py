"""Comprehensive API tests for Baobab AI backend."""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from models.database_models import User
from services.database_service import UserService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "country": "Kenya",
        "job_title": "Developer",
        "ai_interests": ["Machine Learning", "NLP"]
    }

class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "Baobab AI Backend"}

class TestAuthenticationAPI:
    """Test authentication endpoints."""
    
    def test_user_registration(self, client, test_user_data):
        """Test user registration."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_duplicate_user_registration(self, client, test_user_data):
        """Test duplicate user registration fails."""
        # Register first user
        client.post("/api/auth/register", json=test_user_data)
        
        # Try to register same user again
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_user_login(self, client, test_user_data):
        """Test user login."""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
    
    def test_invalid_login(self, client, test_user_data):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client, test_user_data):
        """Test getting current user profile."""
        # Register and login
        register_response = client.post("/api/auth/register", json=test_user_data)
        token = register_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoint."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # No auth header
    
    def test_invalid_token(self, client):
        """Test access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

class TestChatAPI:
    """Test chat endpoints."""
    
    def test_legacy_rag_endpoint(self, client):
        """Test legacy RAG endpoint."""
        question_data = {
            "question": "What is entrepreneurship?",
            "history": []
        }
        response = client.post("/rag", json=question_data)
        assert response.status_code == 200
        assert "answer" in response.json()
    
    def test_rag_with_history(self, client):
        """Test RAG endpoint with conversation history."""
        question_data = {
            "question": "Tell me more about that",
            "history": [
                {"role": "user", "message": "What is AI?"},
                {"role": "assistant", "message": "AI stands for Artificial Intelligence..."}
            ]
        }
        response = client.post("/rag", json=question_data)
        assert response.status_code == 200
        assert "answer" in response.json()

class TestDatabaseService:
    """Test database service functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = UserService.get_password_hash(password)
        
        assert hashed != password
        assert UserService.verify_password(password, hashed)
        assert not UserService.verify_password("wrongpassword", hashed)
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification."""
        data = {"sub": "testuser"}
        token = UserService.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically longer

class TestInputValidation:
    """Test input validation and error handling."""
    
    def test_invalid_email_format(self, client):
        """Test registration with invalid email format."""
        invalid_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpassword123",
            "full_name": "Test User",
            "country": "Kenya"
        }
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # Missing password and other required fields
        }
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_empty_question(self, client):
        """Test RAG endpoint with empty question."""
        question_data = {
            "question": "",
            "history": []
        }
        response = client.post("/rag", json=question_data)
        # Should either handle gracefully or return appropriate error
        assert response.status_code in [200, 400, 422]

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method."""
        response = client.get("/api/auth/register")  # Should be POST
        assert response.status_code == 405

# Performance and load tests
class TestPerformance:
    """Test performance characteristics."""
    
    def test_concurrent_registrations(self, client):
        """Test handling concurrent user registrations."""
        import threading
        import time
        
        results = []
        
        def register_user(index):
            user_data = {
                "username": f"testuser{index}",
                "email": f"test{index}@example.com",
                "password": "testpassword123",
                "full_name": f"Test User {index}",
                "country": "Kenya"
            }
            response = client.post("/api/auth/register", json=user_data)
            results.append(response.status_code)
        
        # Create multiple threads for concurrent registrations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All registrations should succeed
        assert all(status == 200 for status in results)
    
    def test_rag_response_time(self, client):
        """Test RAG endpoint response time."""
        import time
        
        question_data = {
            "question": "What is artificial intelligence?",
            "history": []
        }
        
        start_time = time.time()
        response = client.post("/rag", json=question_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30  # Should respond within 30 seconds

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])