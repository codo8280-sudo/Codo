begin;

-- CODO uses its own FastAPI service as the public data boundary.
-- When deployed on Supabase, keep the generated Data API closed for all CODO
-- tables. The statements are conditional so this migration stays portable to
-- standard PostgreSQL installations where Supabase roles do not exist.
do $$
declare
  table_name text;
  role_name text;
  tables text[] := array[
    'legal_sources','legal_domains','legal_documents','legal_document_versions',
    'legal_articles','legal_article_versions','legal_relationships','institutions',
    'jurisdictions','case_law','procedures','procedure_steps','required_documents',
    'practical_situations','source_snapshots','ai_answers','citations','legal_reviews',
    'audit_logs','procedure_citations','institution_procedures','legal_change_events',
    'user_profiles','user_accessibility_settings','user_favorites','user_search_history',
    'user_folders','user_folder_items','user_alert_subscriptions','notification_deliveries',
    'admin_roles','admin_memberships','ingestion_jobs','ingestion_artifacts','legal_chunks',
    'ingestion_job_events','legal_version_sources','source_registry_checks',
    'legal_relationship_candidates','legal_relationship_evidence','admin_security_events',
    'privacy_events','corpus_publication_receipts','staging_release_runs',
    'staging_release_checks','codo_schema_migrations'
  ];
  roles text[] := array['anon','authenticated','service_role'];
begin
  foreach table_name in array tables loop
    if to_regclass(format('public.%I', table_name)) is not null then
      execute format('alter table public.%I enable row level security', table_name);
      foreach role_name in array roles loop
        if exists (select 1 from pg_roles where rolname = role_name) then
          execute format('revoke all privileges on table public.%I from %I', table_name, role_name);
        end if;
      end loop;
    end if;
  end loop;

  foreach role_name in array roles loop
    if exists (select 1 from pg_roles where rolname = role_name) then
      execute format('alter default privileges in schema public revoke all on tables from %I', role_name);
      execute format('alter default privileges in schema public revoke all on sequences from %I', role_name);
      execute format('alter default privileges in schema public revoke all on functions from %I', role_name);
    end if;
  end loop;
end
$$;

-- Trigger helper functions do not need to be callable through PUBLIC/Data API.
revoke all on function public.codo_refresh_chunk_search_text() from public;
revoke all on function public.codo_refresh_article_search_text() from public;
revoke all on function public.codo_refresh_document_search_text() from public;

commit;
