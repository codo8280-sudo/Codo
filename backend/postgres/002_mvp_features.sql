begin;

alter table legal_sources add column if not exists probative_note text;
alter table legal_sources add column if not exists verified_at timestamptz;
alter table legal_sources add column if not exists last_checked_at timestamptz;
alter table legal_sources add column if not exists terms_note text;

alter table legal_documents add column if not exists search_text tsvector;
alter table legal_article_versions add column if not exists search_text tsvector;

create index if not exists idx_legal_documents_search on legal_documents using gin(search_text);
create index if not exists idx_article_versions_search on legal_article_versions using gin(search_text);

create table if not exists procedure_citations (
  id bigint generated always as identity primary key,
  procedure_id bigint not null references procedures(id) on delete cascade,
  step_id bigint references procedure_steps(id) on delete cascade,
  source_id bigint not null references legal_sources(id),
  document_id bigint references legal_documents(id),
  document_version_id bigint references legal_document_versions(id),
  article_id bigint references legal_articles(id),
  article_version_id bigint references legal_article_versions(id),
  note text,
  unique(procedure_id, step_id, source_id, document_version_id, article_version_id)
);

create table if not exists institution_procedures (
  institution_id bigint not null references institutions(id) on delete cascade,
  procedure_id bigint not null references procedures(id) on delete cascade,
  source_id bigint not null references legal_sources(id),
  verified_at timestamptz,
  primary key (institution_id, procedure_id)
);

create table if not exists legal_change_events (
  id bigint generated always as identity primary key,
  document_id bigint not null references legal_documents(id) on delete cascade,
  article_id bigint references legal_articles(id) on delete cascade,
  event_type text not null check (event_type in ('created','amended','repealed','replaced','suspended','status_changed','verification_updated')),
  from_version_id bigint references legal_document_versions(id),
  to_version_id bigint references legal_document_versions(id),
  effective_date date,
  source_id bigint not null references legal_sources(id),
  verified_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_change_events_document on legal_change_events(document_id, effective_date desc, id desc);

create table if not exists user_profiles (
  id uuid primary key,
  auth_subject text not null unique,
  display_name text,
  locale text not null default 'fr-CI',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists user_accessibility_settings (
  user_id uuid primary key references user_profiles(id) on delete cascade,
  text_scale numeric(3,2) not null default 1.00 check (text_scale between 0.80 and 1.80),
  high_contrast boolean not null default false,
  reduce_motion boolean not null default false,
  offline_cache_enabled boolean not null default false,
  updated_at timestamptz not null default now()
);

create table if not exists user_favorites (
  id bigint generated always as identity primary key,
  user_id uuid not null references user_profiles(id) on delete cascade,
  entity_type text not null check (entity_type in ('document','article','procedure','institution','case_law')),
  entity_key text not null,
  created_at timestamptz not null default now(),
  unique(user_id, entity_type, entity_key)
);

create table if not exists user_search_history (
  id bigint generated always as identity primary key,
  user_id uuid not null references user_profiles(id) on delete cascade,
  query_text text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_search_history_user on user_search_history(user_id, created_at desc);

create table if not exists user_folders (
  id uuid primary key,
  user_id uuid not null references user_profiles(id) on delete cascade,
  name text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists user_folder_items (
  id bigint generated always as identity primary key,
  folder_id uuid not null references user_folders(id) on delete cascade,
  entity_type text not null check (entity_type in ('document','article','procedure','institution','case_law','search')),
  entity_key text not null,
  created_at timestamptz not null default now(),
  unique(folder_id, entity_type, entity_key)
);

create table if not exists user_alert_subscriptions (
  id uuid primary key,
  user_id uuid not null references user_profiles(id) on delete cascade,
  scope_type text not null check (scope_type in ('domain','document','article','topic')),
  scope_key text not null,
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  unique(user_id, scope_type, scope_key)
);

create table if not exists notification_deliveries (
  id bigint generated always as identity primary key,
  subscription_id uuid not null references user_alert_subscriptions(id) on delete cascade,
  change_event_id bigint not null references legal_change_events(id) on delete cascade,
  channel text not null check (channel in ('in_app','email','push')),
  status text not null check (status in ('pending','sent','failed','suppressed')),
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  unique(subscription_id, change_event_id, channel)
);

create table if not exists admin_roles (
  role_key text primary key check (role_key in ('SUPER_ADMIN','RESPONSABLE_JURIDIQUE','VALIDATEUR_JURIDIQUE','DOCUMENTALISTE','REDACTEUR','DATA_MANAGER','MODERATEUR','AUDITEUR')),
  description text not null
);

insert into admin_roles(role_key, description) values
  ('SUPER_ADMIN','Administration générale du système'),
  ('RESPONSABLE_JURIDIQUE','Supervision du corpus juridique'),
  ('VALIDATEUR_JURIDIQUE','Validation des textes et métadonnées'),
  ('DOCUMENTALISTE','Importation et structuration documentaire'),
  ('REDACTEUR','Explications simplifiées et procédures'),
  ('DATA_MANAGER','Gestion et qualité des données'),
  ('MODERATEUR','Supervision des contenus utilisateurs'),
  ('AUDITEUR','Consultation des historiques et journaux sans modification')
on conflict (role_key) do update set description = excluded.description;

create table if not exists admin_memberships (
  id bigint generated always as identity primary key,
  auth_subject text not null,
  role_key text not null references admin_roles(role_key),
  active boolean not null default true,
  granted_at timestamptz not null default now(),
  granted_by text,
  unique(auth_subject, role_key)
);

create table if not exists ingestion_jobs (
  id uuid primary key,
  source_id bigint not null references legal_sources(id),
  source_url text not null,
  status text not null check (status in ('imported','to_analyze','structured','sources_verified','legal_review','validated','published','monitored','failed')),
  content_hash text,
  original_storage_uri text,
  error_message text,
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_ingestion_jobs_status on ingestion_jobs(status, created_at);

create table if not exists ingestion_artifacts (
  id bigint generated always as identity primary key,
  ingestion_job_id uuid not null references ingestion_jobs(id) on delete cascade,
  artifact_type text not null check (artifact_type in ('original','extracted_text','structured_json','review_report','diff_report')),
  storage_uri text not null,
  content_hash text,
  created_at timestamptz not null default now()
);

create or replace function codo_refresh_document_search_text() returns trigger language plpgsql as $$
begin
  new.search_text := to_tsvector('french', coalesce(new.title,'') || ' ' || coalesce(new.document_number,'') || ' ' || coalesce(new.authority_name,''));
  return new;
end;
$$;

drop trigger if exists trg_legal_documents_search on legal_documents;
create trigger trg_legal_documents_search before insert or update of title, document_number, authority_name on legal_documents
for each row execute function codo_refresh_document_search_text();

create or replace function codo_refresh_article_search_text() returns trigger language plpgsql as $$
begin
  new.search_text := to_tsvector('french', coalesce(new.official_text,'') || ' ' || coalesce(new.explanation_codo,'') || ' ' || coalesce(new.short_summary,''));
  return new;
end;
$$;

drop trigger if exists trg_article_versions_search on legal_article_versions;
create trigger trg_article_versions_search before insert or update of official_text, explanation_codo, short_summary on legal_article_versions
for each row execute function codo_refresh_article_search_text();

update legal_documents
set search_text = to_tsvector('french', coalesce(title,'') || ' ' || coalesce(document_number,'') || ' ' || coalesce(authority_name,''))
where search_text is null;

update legal_article_versions
set search_text = to_tsvector('french', coalesce(official_text,'') || ' ' || coalesce(explanation_codo,'') || ' ' || coalesce(short_summary,''))
where search_text is null;

commit;
