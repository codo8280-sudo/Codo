begin;

create table if not exists legal_sources (
  id bigint generated always as identity primary key,
  source_key text not null unique,
  name text not null,
  institution_name text,
  official_url text not null,
  trust_level text not null check (trust_level in ('A','B','C','D')),
  is_official boolean not null default false,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists legal_domains (
  id bigint generated always as identity primary key,
  slug text not null unique,
  name text not null,
  parent_id bigint references legal_domains(id),
  active boolean not null default true
);

create table if not exists legal_documents (
  id bigint generated always as identity primary key,
  codo_id text not null unique,
  domain_id bigint references legal_domains(id),
  source_id bigint not null references legal_sources(id),
  nature text not null,
  title text not null,
  document_number text,
  adoption_date date,
  publication_date date,
  current_status text not null,
  authority_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists legal_document_versions (
  id bigint generated always as identity primary key,
  document_id bigint not null references legal_documents(id),
  version_key text not null,
  valid_from date,
  valid_to date,
  status text not null,
  official_text text not null,
  source_snapshot_uri text,
  is_current boolean not null default false,
  published_at timestamptz,
  unique(document_id, version_key)
);

create table if not exists legal_articles (
  id bigint generated always as identity primary key,
  codo_id text not null unique,
  document_id bigint not null references legal_documents(id),
  article_label text not null,
  sort_order integer not null default 0
);

create table if not exists legal_article_versions (
  id bigint generated always as identity primary key,
  article_id bigint not null references legal_articles(id),
  document_version_id bigint not null references legal_document_versions(id),
  official_text text not null,
  status text not null,
  valid_from date,
  valid_to date,
  explanation_codo text,
  short_summary text,
  is_current boolean not null default false,
  unique(article_id, document_version_id)
);

create table if not exists legal_relationships (
  id bigint generated always as identity primary key,
  from_document_id bigint references legal_documents(id),
  from_article_id bigint references legal_articles(id),
  relation_type text not null,
  to_document_id bigint references legal_documents(id),
  to_article_id bigint references legal_articles(id),
  effective_date date,
  evidence_source_id bigint references legal_sources(id),
  note text
);

create table if not exists institutions (
  id bigint generated always as identity primary key,
  name text not null,
  institution_type text not null,
  official_url text,
  public_address text,
  public_contacts text,
  competencies text,
  source_id bigint references legal_sources(id),
  verified_at timestamptz
);

create table if not exists jurisdictions (
  id bigint generated always as identity primary key,
  institution_id bigint references institutions(id),
  name text not null,
  jurisdiction_type text not null,
  territory text,
  source_id bigint references legal_sources(id),
  verified_at timestamptz
);

create table if not exists case_law (
  id bigint generated always as identity primary key,
  jurisdiction_id bigint references jurisdictions(id),
  source_id bigint not null references legal_sources(id),
  decision_number text,
  decision_date date,
  matter text,
  facts text,
  legal_question text,
  decision_summary text,
  official_text text,
  source_url text,
  verified_at timestamptz
);

create table if not exists procedures (
  id bigint generated always as identity primary key,
  slug text not null unique,
  title text not null,
  domain_id bigint references legal_domains(id),
  summary text,
  status text not null default 'draft',
  validated_at timestamptz
);

create table if not exists procedure_steps (
  id bigint generated always as identity primary key,
  procedure_id bigint not null references procedures(id),
  step_order integer not null,
  title text not null,
  description text,
  authority_institution_id bigint references institutions(id),
  unique(procedure_id, step_order)
);

create table if not exists required_documents (
  id bigint generated always as identity primary key,
  procedure_id bigint not null references procedures(id),
  step_id bigint references procedure_steps(id),
  name text not null,
  requirement_note text,
  source_id bigint references legal_sources(id)
);

create table if not exists practical_situations (
  id bigint generated always as identity primary key,
  slug text not null unique,
  category text not null,
  user_phrase text not null,
  mapped_domain_id bigint references legal_domains(id),
  active boolean not null default true
);

create table if not exists source_snapshots (
  id bigint generated always as identity primary key,
  source_id bigint not null references legal_sources(id),
  captured_at timestamptz not null default now(),
  source_url text not null,
  content_hash text not null,
  storage_uri text not null,
  unique(source_id, content_hash)
);

create table if not exists ai_answers (
  id bigint generated always as identity primary key,
  question_text text not null,
  answer_text text not null,
  has_sufficient_verified_sources boolean not null,
  created_at timestamptz not null default now()
);

create table if not exists citations (
  id bigint generated always as identity primary key,
  ai_answer_id bigint not null references ai_answers(id),
  source_id bigint not null references legal_sources(id),
  document_id bigint references legal_documents(id),
  document_version_id bigint references legal_document_versions(id),
  article_id bigint references legal_articles(id),
  article_version_id bigint references legal_article_versions(id),
  citation_order integer not null
);

create table if not exists legal_reviews (
  id bigint generated always as identity primary key,
  entity_type text not null,
  entity_id bigint not null,
  workflow_status text not null,
  reviewer_subject text,
  review_note text,
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id bigint generated always as identity primary key,
  actor_subject text,
  action text not null,
  entity_type text not null,
  entity_id text not null,
  previous_data jsonb,
  new_data jsonb,
  occurred_at timestamptz not null default now()
);

create index if not exists idx_legal_documents_domain on legal_documents(domain_id);
create index if not exists idx_legal_documents_source on legal_documents(source_id);
create index if not exists idx_document_versions_current on legal_document_versions(document_id, is_current);
create index if not exists idx_article_versions_current on legal_article_versions(article_id, is_current);
create index if not exists idx_procedure_steps_order on procedure_steps(procedure_id, step_order);
create index if not exists idx_audit_logs_entity on audit_logs(entity_type, entity_id, occurred_at desc);

commit;
