begin;

create table if not exists legal_relationship_candidates (
  id uuid primary key,
  from_document_codo_id text not null,
  relation_type text not null check (
    relation_type in ('modifies','repeals','replaces','implements','complements','cites')
  ),
  to_document_codo_id text not null,
  effective_date date,
  evidence_source_key text not null,
  evidence_url text,
  note text,
  status text not null default 'pending' check (status in ('pending','validated','rejected')),
  created_by text,
  created_at timestamptz not null default now(),
  reviewed_by text,
  reviewed_at timestamptz,
  review_note text,
  relationship_id bigint references legal_relationships(id),
  unique(from_document_codo_id, relation_type, to_document_codo_id, evidence_source_key)
);

create index if not exists idx_relationship_candidates_status
  on legal_relationship_candidates(status, created_at);
create index if not exists idx_relationship_candidates_documents
  on legal_relationship_candidates(from_document_codo_id, to_document_codo_id);

create table if not exists legal_relationship_evidence (
  id bigint generated always as identity primary key,
  relationship_id bigint not null references legal_relationships(id) on delete cascade,
  source_id bigint not null references legal_sources(id) on delete restrict,
  candidate_id uuid not null unique references legal_relationship_candidates(id) on delete cascade,
  evidence_url text,
  note text,
  linked_at timestamptz not null default now(),
  unique(relationship_id, source_id, evidence_url)
);

create index if not exists idx_legal_relationship_evidence_relationship
  on legal_relationship_evidence(relationship_id, linked_at);

create index if not exists idx_admin_memberships_subject_active
  on admin_memberships(auth_subject, active, role_key);

create table if not exists admin_security_events (
  id bigint generated always as identity primary key,
  actor_subject text,
  event_type text not null check (
    event_type in ('membership_granted','membership_revoked','relationship_validated','relationship_rejected')
  ),
  target_subject text,
  metadata jsonb,
  occurred_at timestamptz not null default now()
);

create index if not exists idx_admin_security_events_subject
  on admin_security_events(actor_subject, occurred_at desc);

commit;
