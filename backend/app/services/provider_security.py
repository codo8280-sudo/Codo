from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

CODO_PUBLIC_TABLES: tuple[str, ...] = (
    'legal_sources', 'legal_domains', 'legal_documents', 'legal_document_versions',
    'legal_articles', 'legal_article_versions', 'legal_relationships', 'institutions',
    'jurisdictions', 'case_law', 'procedures', 'procedure_steps', 'required_documents',
    'practical_situations', 'source_snapshots', 'ai_answers', 'citations', 'legal_reviews',
    'audit_logs', 'procedure_citations', 'institution_procedures', 'legal_change_events',
    'user_profiles', 'user_accessibility_settings', 'user_favorites', 'user_search_history',
    'user_folders', 'user_folder_items', 'user_alert_subscriptions', 'notification_deliveries',
    'admin_roles', 'admin_memberships', 'ingestion_jobs', 'ingestion_artifacts', 'legal_chunks',
    'ingestion_job_events', 'legal_version_sources', 'source_registry_checks',
    'legal_relationship_candidates', 'legal_relationship_evidence', 'admin_security_events',
    'privacy_events', 'corpus_publication_receipts', 'staging_release_runs',
    'staging_release_checks', 'codo_schema_migrations',
)

SUPABASE_DATA_API_ROLES: tuple[str, ...] = ('anon', 'authenticated', 'service_role')


@dataclass(frozen=True)
class TableSecurityState:
    table_name: str
    rls_enabled: bool


@dataclass(frozen=True)
class TableGrant:
    grantee: str
    table_name: str
    privilege_type: str


def evaluate_supabase_security(
    *,
    table_states: Iterable[TableSecurityState],
    grants: Iterable[TableGrant],
    existing_roles: Iterable[str],
) -> list[str]:
    issues: list[str] = []
    states = {item.table_name: item.rls_enabled for item in table_states}
    missing_tables = [name for name in CODO_PUBLIC_TABLES if name not in states]
    if missing_tables:
        issues.append('missing_tables=' + ','.join(sorted(missing_tables)))

    rls_missing = [name for name in CODO_PUBLIC_TABLES if states.get(name) is False]
    if rls_missing:
        issues.append('rls_disabled=' + ','.join(sorted(rls_missing)))

    roles = set(existing_roles)
    missing_roles = [name for name in SUPABASE_DATA_API_ROLES if name not in roles]
    if missing_roles:
        issues.append('missing_supabase_roles=' + ','.join(sorted(missing_roles)))

    leaked = [
        f'{grant.grantee}:{grant.table_name}:{grant.privilege_type}'
        for grant in grants
        if grant.grantee in SUPABASE_DATA_API_ROLES and grant.table_name in CODO_PUBLIC_TABLES
    ]
    if leaked:
        issues.append('data_api_grants=' + ','.join(sorted(leaked)))
    return issues
