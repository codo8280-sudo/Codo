from __future__ import annotations

from app.main import app


def test_increment08_version_and_health_provider_are_exposed():
    schema = app.openapi()
    assert schema['info']['version'] == '0.8.0'
    assert '/health' in schema['paths']
    assert '/health/ready' in schema['paths']
