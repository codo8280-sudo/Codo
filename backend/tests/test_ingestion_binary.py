from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.ingestion import IngestionService


def test_manual_pdf_requires_pdf_signature(monkeypatch):
    from app.services import ingestion as module

    monkeypatch.setattr(module, "settings", SimpleNamespace(acquisition_max_bytes=1024))
    with pytest.raises(ValueError, match="PDF signature"):
        IngestionService._validate_body(b"not a pdf", "application/pdf")


def test_manual_pdf_accepts_pdf_signature(monkeypatch):
    from app.services import ingestion as module

    monkeypatch.setattr(module, "settings", SimpleNamespace(acquisition_max_bytes=1024))
    mime = IngestionService._validate_body(b"%PDF-1.7\nminimal", "application/pdf; charset=binary")
    assert mime == "application/pdf"


def test_manual_source_rejects_oversized_body(monkeypatch):
    from app.services import ingestion as module

    monkeypatch.setattr(module, "settings", SimpleNamespace(acquisition_max_bytes=4))
    with pytest.raises(ValueError, match="size limit"):
        IngestionService._validate_body(b"12345", "text/plain")
