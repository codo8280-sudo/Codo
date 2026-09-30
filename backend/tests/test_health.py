from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_liveness_does_not_require_database():
    client = TestClient(app)
    response = client.get('/health/live')
    assert response.status_code == 200
    assert response.json()['status'] == 'alive'


def test_readiness_is_not_green_without_database_and_oidc():
    client = TestClient(app)
    response = client.get('/health/ready')
    assert response.status_code == 503
    assert response.json()['status'] == 'not_ready'


def test_health_does_not_disclose_bootstrap_state():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert 'admin_bootstrap_enabled' not in response.json()
