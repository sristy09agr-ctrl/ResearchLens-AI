"""
Unit and integration tests for ResearchLens AI API routes.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import initialize_database

client = TestClient(app)


def setup_module():
    initialize_database()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "database" in data


def test_list_documents():
    response = client.get("/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "documents" in data


def test_search_validation_empty_query():
    response = client.post("/v1/search", json={"query": ""})
    assert response.status_code in [400, 422]


def test_search_endpoint_with_valid_query():
    response = client.post(
        "/v1/search",
        json={
            "query": "transformer attention mechanisms",
            "top_k": 3,
            "candidate_k": 10,
            "alpha": 0.5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "results" in data

