"""Unit tests for Coffee Brew API.

SCRUM-19: Add unit tests for brew API endpoints.
Target: 80% coverage.
"""
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_caffeinated(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] == "caffeinated"
        assert "timestamp" in data


class TestBrewsEndpoint:
    def test_list_brews_empty(self, client):
        resp = client.get("/brews")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 0
        assert data["brews"] == []

    def test_create_brew_default_strength(self, client):
        resp = client.post("/brews", json={})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["strength"] == "medium"
        assert data["status"] == "brewing"
        assert data["id"] == 1

    def test_create_brew_custom_strength(self, client):
        resp = client.post("/brews", json={"strength": "strong", "roast": "espresso"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["strength"] == "strong"
        assert data["roast"] == "espresso"

    def test_create_brew_invalid_strength(self, client):
        resp = client.post("/brews", json={"strength": "turbo"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_list_brews_after_create(self, client):
        client.post("/brews", json={"strength": "light"})
        resp = client.get("/brews")
        data = resp.get_json()
        assert data["count"] >= 1


class TestGetBrewEndpoint:
    def test_get_brew_not_found(self, client):
        resp = client.get("/brews/9999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"] == "Brew not found"

    def test_get_brew_after_create(self, client):
        create_resp = client.post("/brews", json={"strength": "strong"})
        brew_id = create_resp.get_json()["id"]
        resp = client.get(f"/brews/{brew_id}")
        assert resp.status_code == 200
        assert resp.get_json()["strength"] == "strong"
