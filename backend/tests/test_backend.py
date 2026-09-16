import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_login_seeded_developer():
    response = client.post("/api/auth/login", json={
        "email": "dev@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "developer"

def test_login_invalid_credentials():
    response = client.post("/api/auth/login", json={
        "email": "dev@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_openproject_work_packages_protected():
    # Without token
    response = client.get("/api/openproject/work_packages")
    assert response.status_code == 401

    # With token
    login_res = client.post("/api/auth/login", json={
        "email": "dev@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/openproject/work_packages", headers=headers)
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) >= 1
    ids = [p["id"] for p in packages]
    assert "BUG-101" in ids
