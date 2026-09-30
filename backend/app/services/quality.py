from __future__ import annotations


def blocking_quality_failures(
    *,
    original_preserved: bool,
    source_registry_verified: bool,
    core_metadata_present: bool,
    document_status_final: bool,
    extraction_trace_preserved: bool,
    structured_artifact_preserved: bool,
    normative: bool,
    article_count: int,
    pending_article_count: int,
    provenance_sufficient: bool,
) -> list[str]:
    failures: list[str] = []
    checks = {
        "original_preserved": original_preserved,
        "source_registry_verified": source_registry_verified,
        "core_metadata_present": core_metadata_present,
        "legal_status_decided": document_status_final,
        "extraction_trace_preserved": extraction_trace_preserved,
        "structured_artifact_preserved": structured_artifact_preserved,
        "source_provenance_linked": provenance_sufficient,
    }
    failures.extend(key for key, passed in checks.items() if not passed)
    if normative and article_count < 1:
        failures.append("articles_structured")
    if pending_article_count > 0:
        failures.append("article_legal_status_decided")
    return sorted(set(failures))
