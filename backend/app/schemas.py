from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

LegalStatus = Literal[
    "in_force",
    "partially_in_force",
    "amended",
    "repealed",
    "replaced",
    "suspended",
    "bill",
    "draft_decree",
    "adopted_awaiting_publication",
    "historical",
    "verification_pending",
]

FinalLegalStatus = Literal[
    "in_force",
    "partially_in_force",
    "amended",
    "repealed",
    "replaced",
    "suspended",
    "bill",
    "draft_decree",
    "adopted_awaiting_publication",
    "historical",
]


class LegalSourceOut(BaseModel):
    id: str
    name: str
    institution_name: str | None = None
    trust_level: Literal["A", "B", "C", "D"]
    url: HttpUrl
    is_official: bool
    probative_note: str | None = None
    verified_at: datetime | None = None


class LegalDocumentOut(BaseModel):
    codo_id: str
    title: str
    nature: str
    number: str | None = None
    status: LegalStatus
    source: LegalSourceOut
    adoption_date: date | None = None
    publication_date: date | None = None
    effective_date: date | None = None
    current_version: str | None = None
    authority_name: str | None = None


class LegalArticleOut(BaseModel):
    codo_id: str
    document_id: str
    label: str
    official_text: str
    status: LegalStatus
    version: str
    source: LegalSourceOut
    explanation_codo: str | None = None
    short_summary: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None


class ArticleVersionOut(BaseModel):
    version_key: str
    status: LegalStatus
    official_text: str
    valid_from: date | None = None
    valid_to: date | None = None
    is_current: bool = False


class ProvenanceSourceOut(BaseModel):
    source_id: str
    source_name: str
    institution_name: str | None = None
    trust_level: Literal["A", "B", "C"]
    provenance_role: Literal["primary_text", "amendment", "verification", "historical_reference"]
    source_url: HttpUrl
    final_url: HttpUrl | None = None
    captured_at: datetime
    content_hash: str
    verified_at: datetime | None = None
    note: str | None = None


class DocumentProvenanceOut(BaseModel):
    document_id: str
    version_key: str
    sources: list[ProvenanceSourceOut]




class PublicationReceiptOut(BaseModel):
    document_id: str
    version_key: str
    publication_hash: str = Field(min_length=64, max_length=64)
    source_snapshot_hash: str = Field(min_length=64, max_length=64)
    published_at: datetime

class CitationOut(BaseModel):
    source_id: str
    document_id: str
    article_id: str | None = None
    version: str
    label: str | None = None
    source_url: HttpUrl | None = None
    trust_level: Literal["A", "B", "C"] | None = None


class SearchResultOut(BaseModel):
    document: LegalDocumentOut
    article: LegalArticleOut | None = None
    snippet: str
    score: float | None = None
    retrieval_kind: Literal["lexical", "semantic", "hybrid"] = "lexical"


class SearchResponse(BaseModel):
    results: list[SearchResultOut]
    semantic_search_used: bool = False


class AnswerRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    mode: Literal["simple", "detailed", "legal", "professional"] = "simple"


class CodoAnswerOut(BaseModel):
    situation: str
    law_summary: str
    next_steps: list[str] = Field(default_factory=list)
    documents_needed: list[str] = Field(default_factory=list)
    where_to_act: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    attention_points: list[str] = Field(default_factory=list)
    citations: list[CitationOut] = Field(default_factory=list)
    has_sufficient_verified_sources: bool
    answer_mode: str = "simple"


class AcquisitionRequest(BaseModel):
    source_key: str = Field(min_length=2, max_length=120)
    source_url: HttpUrl


class AcquisitionResponse(BaseModel):
    job_id: str
    source_key: str
    source_url: HttpUrl
    final_url: HttpUrl
    content_hash: str
    byte_size: int
    mime_type: str
    status: str
    storage_uri: str


class ExtractionResponse(BaseModel):
    job_id: str
    text_path: str
    content_hash: str
    page_count: int | None = None
    char_count: int
    status: Literal["to_analyze"] = "to_analyze"


class DraftMetadataIn(BaseModel):
    codo_id: str = Field(min_length=4, max_length=180)
    domain_slug: str | None = None
    nature: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1)
    document_number: str | None = None
    authority_name: str | None = None
    adoption_date: date | None = None
    publication_date: date | None = None
    version_key: str = Field(min_length=1, max_length=180)
    valid_from: date | None = None
    valid_to: date | None = None


class DraftDiagnosticsOut(BaseModel):
    article_count: int
    duplicate_labels: list[str] = Field(default_factory=list)
    numeric_gaps: list[int] = Field(default_factory=list)
    first_article_number: int | None = None
    last_article_number: int | None = None
    warnings: list[str] = Field(default_factory=list)


class StructuredArticleIn(BaseModel):
    codo_id: str = Field(min_length=4, max_length=180)
    label: str = Field(min_length=1, max_length=180)
    official_text: str = Field(min_length=1)
    status: LegalStatus
    valid_from: date | None = None
    valid_to: date | None = None
    explanation_codo: str | None = None
    short_summary: str | None = None
    sort_order: int = 0


class StructuredDocumentIn(BaseModel):
    source_snapshot_hash: str = Field(min_length=64, max_length=64)
    codo_id: str = Field(min_length=4, max_length=180)
    domain_slug: str | None = None
    nature: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1)
    document_number: str | None = None
    status: LegalStatus
    authority_name: str | None = None
    adoption_date: date | None = None
    publication_date: date | None = None
    version_key: str = Field(min_length=1, max_length=180)
    valid_from: date | None = None
    valid_to: date | None = None
    official_text: str = Field(min_length=1)
    articles: list[StructuredArticleIn] = Field(default_factory=list)


class DraftResponse(BaseModel):
    package: StructuredDocumentIn
    diagnostics: DraftDiagnosticsOut


class StructureResponse(BaseModel):
    job_id: str
    document_codo_id: str
    document_version_id: int
    article_version_count: int
    status: str


class WorkflowTransitionRequest(BaseModel):
    target_status: Literal[
        "to_analyze", "structured", "sources_verified", "legal_review",
        "validated", "published", "monitored"
    ]
    note: str | None = Field(default=None, max_length=2000)


class WorkflowTransitionResponse(BaseModel):
    job_id: str
    previous_status: str
    status: str


class LegalDecisionRequest(BaseModel):
    document_status: FinalLegalStatus
    article_default_status: FinalLegalStatus | None = None
    article_statuses: dict[str, FinalLegalStatus] = Field(default_factory=dict)
    valid_from: date | None = None
    note: str | None = Field(default=None, max_length=2000)


class LegalDecisionResponse(BaseModel):
    job_id: str
    document_status: FinalLegalStatus
    article_version_count: int
    status: str


class QualityCheckOut(BaseModel):
    key: str
    passed: bool
    blocking: bool
    detail: str


class QualityReportResponse(BaseModel):
    job_id: str
    workflow_status: str
    can_validate: bool
    can_publish: bool
    checks: list[QualityCheckOut]


class IngestionArtifactOut(BaseModel):
    artifact_type: str
    storage_uri: str
    content_hash: str | None = None
    created_at: datetime


class IngestionEventOut(BaseModel):
    from_status: str | None = None
    to_status: str
    actor_subject: str | None = None
    note: str | None = None
    occurred_at: datetime


class IngestionJobOut(BaseModel):
    job_id: str
    source_key: str
    source_url: HttpUrl
    final_url: HttpUrl | None = None
    status: str
    content_hash: str | None = None
    mime_type: str | None = None
    byte_size: int | None = None
    created_at: datetime
    updated_at: datetime
    artifacts: list[IngestionArtifactOut] = Field(default_factory=list)
    events: list[IngestionEventOut] = Field(default_factory=list)

AdminRole = Literal[
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "VALIDATEUR_JURIDIQUE",
    "DOCUMENTALISTE",
    "REDACTEUR",
    "DATA_MANAGER",
    "MODERATEUR",
    "AUDITEUR",
]


class AdminPrincipalOut(BaseModel):
    subject: str
    roles: list[AdminRole]
    authentication_method: Literal["oidc", "bootstrap"]


class AdminMembershipGrantIn(BaseModel):
    auth_subject: str = Field(min_length=1, max_length=512)
    role_key: AdminRole


class AdminMembershipOut(BaseModel):
    auth_subject: str
    role_key: AdminRole
    active: bool
    granted_at: datetime
    granted_by: str | None = None


RelationshipType = Literal[
    "modifies",
    "repeals",
    "replaces",
    "implements",
    "complements",
    "cites",
]


class RelationshipCandidateIn(BaseModel):
    from_document_codo_id: str = Field(min_length=4, max_length=180)
    relation_type: RelationshipType
    to_document_codo_id: str = Field(min_length=4, max_length=180)
    effective_date: date | None = None
    evidence_source_key: str = Field(min_length=2, max_length=120)
    evidence_url: HttpUrl | None = None
    note: str | None = Field(default=None, max_length=4000)


class RelationshipCandidateReviewIn(BaseModel):
    approved: bool
    note: str | None = Field(default=None, max_length=4000)


class RelationshipCandidateOut(BaseModel):
    id: str
    from_document_codo_id: str
    relation_type: RelationshipType
    to_document_codo_id: str
    effective_date: date | None = None
    evidence_source_key: str
    evidence_url: HttpUrl | None = None
    status: Literal["pending", "validated", "rejected"]
    created_by: str | None = None
    created_at: datetime
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None
    relationship_id: int | None = None


class LegalRelationshipOut(BaseModel):
    id: int
    from_document_codo_id: str | None = None
    from_article_codo_id: str | None = None
    relation_type: str
    to_document_codo_id: str | None = None
    to_article_codo_id: str | None = None
    effective_date: date | None = None
    evidence_source_key: str | None = None
    evidence_source_name: str | None = None
    note: str | None = None

class LegalRelationshipsResponse(BaseModel):
    items: list[LegalRelationshipOut]


class UserProfileOut(BaseModel):
    id: str
    auth_subject: str
    auth_issuer: str
    display_name: str | None = None
    email: str | None = None
    email_verified: bool = False
    locale: str = "fr-CI"
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None


class UserProfileUpdateIn(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=240)
    locale: str | None = Field(default=None, min_length=2, max_length=32)


class AccessibilitySettingsIn(BaseModel):
    text_scale: float = Field(default=1.0, ge=0.8, le=1.8)
    high_contrast: bool = False
    reduce_motion: bool = False
    offline_cache_enabled: bool = False


class AccessibilitySettingsOut(AccessibilitySettingsIn):
    updated_at: datetime


FavoriteEntityType = Literal["document", "article", "procedure", "institution", "case_law"]


class FavoriteIn(BaseModel):
    entity_type: FavoriteEntityType
    entity_key: str = Field(min_length=1, max_length=240)


class FavoriteOut(BaseModel):
    id: int
    entity_type: FavoriteEntityType
    entity_key: str
    created_at: datetime

FolderEntityType = Literal["document", "article", "procedure", "institution", "case_law", "search"]


class UserFolderCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)


class UserFolderOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    item_count: int = 0
    created_at: datetime
    updated_at: datetime


class UserFolderItemIn(BaseModel):
    entity_type: FolderEntityType
    entity_key: str = Field(min_length=1, max_length=240)


class UserFolderItemOut(BaseModel):
    id: int
    entity_type: FolderEntityType
    entity_key: str
    created_at: datetime


AlertScopeType = Literal["domain", "document", "article", "topic"]


class UserAlertCreateIn(BaseModel):
    scope_type: AlertScopeType
    scope_key: str = Field(min_length=1, max_length=240)


class UserAlertUpdateIn(BaseModel):
    enabled: bool


class UserAlertOut(BaseModel):
    id: str
    scope_type: AlertScopeType
    scope_key: str
    enabled: bool
    created_at: datetime
