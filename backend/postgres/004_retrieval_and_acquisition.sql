begin;

-- pgvector is optional at migration time. PostgreSQL deployments that provide
-- the extension gain semantic retrieval; otherwise lexical retrieval stays available.
do $$
begin
  create extension if not exists vector;
exception
  when undefined_file or insufficient_privilege then
    raise notice 'pgvector extension is not installed; semantic retrieval remains disabled.';
end
$$;

create table if not exists legal_chunks (
  id bigint generated always as identity primary key,
  document_version_id bigint not null references legal_document_versions(id) on delete cascade,
  article_version_id bigint not null references legal_article_versions(id) on delete cascade,
  source_id bigint not null references legal_sources(id),
  chunk_index integer not null,
  chunk_text text not null,
  search_text tsvector,
  content_hash text not null,
  embedding_model text,
  embedding_dimensions integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(article_version_id, chunk_index, content_hash)
);

create index if not exists idx_legal_chunks_search on legal_chunks using gin(search_text);
create index if not exists idx_legal_chunks_article_version on legal_chunks(article_version_id, chunk_index);
create index if not exists idx_legal_chunks_model_dims on legal_chunks(embedding_model, embedding_dimensions);

create or replace function codo_refresh_chunk_search_text() returns trigger language plpgsql as $$
begin
  new.search_text := to_tsvector('french', coalesce(new.chunk_text,''));
  new.updated_at := now();
  return new;
end;
$$;

drop trigger if exists trg_legal_chunks_search on legal_chunks;
create trigger trg_legal_chunks_search before insert or update of chunk_text on legal_chunks
for each row execute function codo_refresh_chunk_search_text();

-- Add the vector column only when pgvector is available. This keeps the core
-- database portable and makes semantic search an explicit capability.
do $$
begin
  if exists (select 1 from pg_type where typname = 'vector') then
    if not exists (
      select 1 from information_schema.columns
      where table_name='legal_chunks' and column_name='embedding'
    ) then
      execute 'alter table legal_chunks add column embedding vector';
    end if;
  end if;
end
$$;

alter table source_snapshots add column if not exists final_url text;
alter table source_snapshots add column if not exists mime_type text;
alter table source_snapshots add column if not exists byte_size bigint;
alter table source_snapshots add column if not exists http_etag text;
alter table source_snapshots add column if not exists http_last_modified text;

alter table ingestion_jobs add column if not exists final_url text;
alter table ingestion_jobs add column if not exists mime_type text;
alter table ingestion_jobs add column if not exists byte_size bigint;
alter table ingestion_jobs add column if not exists http_etag text;
alter table ingestion_jobs add column if not exists http_last_modified text;


alter table legal_document_versions add column if not exists ingestion_job_id uuid references ingestion_jobs(id);
alter table legal_article_versions add column if not exists ingestion_job_id uuid references ingestion_jobs(id);
create index if not exists idx_document_versions_ingestion_job on legal_document_versions(ingestion_job_id);
create index if not exists idx_article_versions_ingestion_job on legal_article_versions(ingestion_job_id);

create table if not exists ingestion_job_events (
  id bigint generated always as identity primary key,
  ingestion_job_id uuid not null references ingestion_jobs(id) on delete cascade,
  from_status text,
  to_status text not null,
  actor_subject text,
  note text,
  occurred_at timestamptz not null default now()
);
create index if not exists idx_ingestion_job_events_job on ingestion_job_events(ingestion_job_id, occurred_at, id);

-- Public retrieval must never be ambiguous about which version is current.
create unique index if not exists uq_document_one_current_version
  on legal_document_versions(document_id) where is_current = true;
create unique index if not exists uq_article_one_current_version
  on legal_article_versions(article_id) where is_current = true;

update legal_chunks
set search_text = to_tsvector('french', coalesce(chunk_text,''))
where search_text is null;

commit;
