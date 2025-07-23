
"""Test suite for Baobab AI backend."""
import pytest
from fastapi.testclient import TestClient
from main import app

def test_rag_endpoint_valid():
    client = TestClient(app)
    payload = {
        "question": "Quelle est la capitale de la France ?",
        "history": [
            {"role": "user", "message": "Bonjour"},
            {"role": "assistant", "message": "Bonjour, comment puis-je vous aider ?"}
        ]
    }
    response = client.post("/rag", json=payload)
    assert response.status_code == 200
    assert "Paris" in response.json()["answer"]

def test_rag_endpoint_invalid_history():
    client = TestClient(app)
    payload = {
        "question": "Test question",
        "history": ["not_a_dict"]
    }
    response = client.post("/rag", json=payload)
    assert response.status_code == 422
    assert "Each history item must be a dict" in response.text

def test_rag_endpoint_missing_keys():
    client = TestClient(app)
    payload = {
        "question": "Test question",
        "history": [{"role": "user"}]
    }
    response = client.post("/rag", json=payload)
    assert response.status_code == 422
    assert "Each history item must have \"role\" and \"message\" keys" in response.text
"""Test suite for Baobab AI backend."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_rag_valid():
    data = {"question": "Quelle est la capitale de la France?", "history": []}
    resp = client.post("/rag", json=data)
    assert resp.status_code == 200
    assert "answer" in resp.json()

def test_rag_invalid():
    data = {"question": 123, "history": "notalist"}
    resp = client.post("/rag", json=data)
    assert resp.status_code == 422
