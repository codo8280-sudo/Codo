begin;

-- First official source used for the current consolidated constitutional corpus.
insert into legal_sources (
  source_key, name, institution_name, official_url, trust_level, is_official,
  probative_note, verified_at, last_checked_at, terms_note
) values (
  'CI-PRESIDENCE',
  'Présidence de la République de Côte d’Ivoire',
  'Présidence de la République de Côte d’Ivoire',
  'https://www.presidence.ci/',
  'A', true,
  'Source institutionnelle primaire. CODO conserve néanmoins le document acquis et son empreinte avant toute validation juridique interne.',
  '2026-09-29T00:00:00Z', '2026-09-29T00:00:00Z',
  'Respecter les conditions d’accès et de réutilisation de la source institutionnelle.'
)
on conflict (source_key) do update set
  name=excluded.name,
  institution_name=excluded.institution_name,
  official_url=excluded.official_url,
  trust_level=excluded.trust_level,
  is_official=excluded.is_official,
  probative_note=excluded.probative_note,
  verified_at=excluded.verified_at,
  last_checked_at=excluded.last_checked_at,
  terms_note=excluded.terms_note,
  updated_at=now();

insert into legal_domains(slug, name, active) values
  ('droit-constitutionnel', 'Droit constitutionnel', true),
  ('droit-penal', 'Droit pénal', true),
  ('procedure-penale', 'Procédure pénale', true),
  ('droit-travail', 'Droit du travail', true),
  ('foncier-immobilier', 'Foncier / immobilier', true),
  ('construction-urbanisme', 'Construction / urbanisme', true),
  ('famille', 'Famille', true),
  ('droit-commercial-ohada', 'Droit commercial et OHADA', true),
  ('recouvrement-creances', 'Recouvrement des créances', true)
on conflict (slug) do update set name=excluded.name, active=excluded.active;

-- A legal version can be supported by more than one captured official source.
-- This is preferable to hiding provenance behind a single source_snapshot_uri.
create table if not exists legal_version_sources (
  id bigint generated always as identity primary key,
  document_version_id bigint not null references legal_document_versions(id) on delete cascade,
  source_snapshot_id bigint not null references source_snapshots(id) on delete restrict,
  provenance_role text not null check (provenance_role in ('primary_text','amendment','verification','historical_reference')),
  note text,
  linked_at timestamptz not null default now(),
  unique(document_version_id, source_snapshot_id, provenance_role)
);

create index if not exists idx_legal_version_sources_version
  on legal_version_sources(document_version_id, provenance_role);

-- Record repeat checks of an institutional source even when content did not change.
create table if not exists source_registry_checks (
  id bigint generated always as identity primary key,
  source_id bigint not null references legal_sources(id) on delete cascade,
  checked_url text not null,
  observed_at timestamptz not null default now(),
  outcome text not null check (outcome in ('reachable','changed','unchanged','redirected','unavailable','manual_review')),
  content_hash text,
  http_status integer,
  note text
);

create index if not exists idx_source_registry_checks_source
  on source_registry_checks(source_id, observed_at desc);

commit;
