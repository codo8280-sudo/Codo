from __future__ import annotations

from app.services.quality import blocking_quality_failures


def test_quality_gate_passes_when_all_blocking_conditions_are_met():
    assert blocking_quality_failures(
        original_preserved=True,
        source_registry_verified=True,
        core_metadata_present=True,
        document_status_final=True,
        extraction_trace_preserved=True,
        structured_artifact_preserved=True,
        normative=True,
        article_count=10,
        pending_article_count=0,
        provenance_sufficient=True,
    ) == []


def test_quality_gate_blocks_missing_trace_and_pending_status():
    failures = blocking_quality_failures(
        original_preserved=True,
        source_registry_verified=True,
        core_metadata_present=True,
        document_status_final=False,
        extraction_trace_preserved=False,
        structured_artifact_preserved=True,
        normative=True,
        article_count=0,
        pending_article_count=2,
        provenance_sufficient=False,
    )
    assert "legal_status_decided" in failures
    assert "extraction_trace_preserved" in failures
    assert "articles_structured" in failures
    assert "article_legal_status_decided" in failures
    assert "source_provenance_linked" in failures
