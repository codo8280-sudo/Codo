begin;

alter table user_profiles add column if not exists auth_issuer text;
alter table user_profiles add column if not exists email text;
alter table user_profiles add column if not exists email_verified boolean not null default false;
alter table user_profiles add column if not exists last_login_at timestamptz;

update user_profiles
set auth_issuer = 'legacy'
where auth_issuer is null;

alter table user_profiles alter column auth_issuer set not null;

create index if not exists idx_user_profiles_issuer_subject
  on user_profiles(auth_issuer, auth_subject);
create index if not exists idx_user_profiles_last_login
  on user_profiles(last_login_at desc nulls last);

-- Privacy events intentionally keep only a one-way hash of the OIDC subject.
-- This allows operational evidence of deletion without retaining the identifier.
create table if not exists privacy_events (
  id bigint generated always as identity primary key,
  subject_hash text not null,
  event_type text not null check (event_type in ('account_deleted')),
  metadata jsonb,
  occurred_at timestamptz not null default now()
);

create index if not exists idx_privacy_events_occurred
  on privacy_events(occurred_at desc);

commit;
