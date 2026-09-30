from __future__ import annotations

from app.main import app


def test_publication_receipt_is_exposed_in_openapi():
    schema = app.openapi()
    assert "/v1/documents/{codo_id}/publication-receipt" in schema["paths"]
    assert schema["info"]["version"] == "0.8.0"
