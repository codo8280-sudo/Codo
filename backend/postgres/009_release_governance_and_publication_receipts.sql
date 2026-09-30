begin;

create table if not exists corpus_publication_receipts (
  id bigint generated always as identity primary key,
  ingestion_job_id uuid not null unique references ingestion_jobs(id) on delete restrict,
  document_version_id bigint not null unique references legal_document_versions(id) on delete restrict,
  document_codo_id text not null,
  version_key text not null,
  publication_hash text not null check (publication_hash ~ '^[0-9a-f]{64}$'),
  source_snapshot_hash text not null check (source_snapshot_hash ~ '^[0-9a-f]{64}$'),
  validator_subject text not null,
  publisher_subject text not null,
  published_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_publication_receipts_document
  on corpus_publication_receipts(document_codo_id, published_at desc);

create table if not exists staging_release_runs (
  id bigint generated always as identity primary key,
  release_label text not null,
  environment_name text not null,
  status text not null check (status in ('running','passed','failed')),
  initiated_by text,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists staging_release_checks (
  id bigint generated always as identity primary key,
  release_run_id bigint not null references staging_release_runs(id) on delete cascade,
  check_key text not null,
  passed boolean not null,
  blocking boolean not null default true,
  detail text,
  checked_at timestamptz not null default now(),
  unique(release_run_id, check_key)
);

create index if not exists idx_staging_release_runs_environment
  on staging_release_runs(environment_name, started_at desc);

commit;
