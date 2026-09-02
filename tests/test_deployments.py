import os
from pathlib import Path
from annotated_types import IsInfinite
import pytest
from database import get_connection

TEST_DB = "test_deploylens.db"

test_db_path = Path(TEST_DB)

if test_db_path.exists():
    test_db_path.unlink()

os.environ["DEPLOYLENS_DB"] = TEST_DB

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
@pytest.fixture(autouse=True)
def clean_database():
    connection = get_connection()

    connection.execute("DELETE FROM deployments")
    connection.commit()
    connection.close()

def test_create_deployment():
    deployment = {
        "service": "payments-api",
        "environment": "prod",
        "version": "1.0.0",
        "status": "healthy"
    }

    response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "payments-api"
    assert data["environment"] == "prod"
    assert data["version"] == "1.0.0"
    assert data["status"] == "healthy"

    assert "id" in data

def test_create_and_get_deployment():
    deployment = {
        "service": "billing-api",
        "environment": "stage",
        "version": "2.0.0",
        "status": "healthy"
    }

    create_response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert create_response.status_code == 200

    get_response = client.get("/api/deployments")

    assert get_response.status_code == 200

    deployments = get_response.json()

    assert any(
        item["service"] == "billing-api"
        for item in deployments
    )

def test_update_deployment():
    deployment = {
        "service": "payments-api",
        "environment": "stage",
        "version": "1.0.0",
        "status": "healthy"
    }

    create_response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert create_response.status_code == 200

    deployment_id = create_response.json()["id"]

    updated_deployment = {
        "service": "payments-api",
        "environment": "prod",
        "version": "2.0.0",
        "status": "degraded"
    }

    update_response = client.put(
        f"/api/deployments/{deployment_id}",
        json=updated_deployment
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == deployment_id
    assert data["environment"] == "prod"
    assert data["version"] == "2.0.0"
    assert data["status"] == "degraded"

    get_response = client.get("/api/deployments")

    assert get_response.status_code == 200

    deployments = get_response.json()

    updated_item = next(
        item
        for item in deployments
        if item["id"] == deployment_id
    )

    assert updated_item["environment"] == "prod"
    assert updated_item["version"] == "2.0.0"
    assert updated_item["status"] == "degraded"

def test_delete_deployment():
    deployment = {
        "service": "legacy-api",
        "environment": "test4",
        "version": "0.1.0",
        "status": "degraded"
    }

    create_response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert create_response.status_code == 200
    
    deployment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/deployments/{deployment_id}"
    )

    assert delete_response.status_code == 200

    get_response = client.get("/api/deployments")

    assert get_response.status_code == 200

    deployments = get_response.json()

    assert all(
        item["id"] != deployment_id
        for item in deployments
    )

def test_delete_nonexistent_deployment():
    response = client.delete(
        "/api/deployments/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Deployment not found"

def test_invalid_environment():
    deployment = {
        "service": "payments-api",
        "environment": "banana",
        "version": "1.0.0",
        "status": "healthy"
    }

    response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert response.status_code == 422

def test_invalid_status():
    deployment = {
        "service": "payments-api",
        "environment": "prod",
        "version": "1.0.0",
        "status": "exploded"
    }

    response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert response.status_code == 422

def test_empty_service():
    deployment = {
        "service": "",
        "environment": "prod",
        "version": "1.0.0",
        "status": "healthy"
    }

    response = client.post(
        "/api/deployments",
        json=deployment
    )

    assert response.status_code == 422

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "reachable"