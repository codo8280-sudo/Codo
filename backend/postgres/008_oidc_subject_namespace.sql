begin;

-- An OIDC subject is only globally meaningful together with its issuer.
-- Keep historical migrations immutable and correct the uniqueness model additively.
alter table user_profiles
  drop constraint if exists user_profiles_auth_subject_key;

create unique index if not exists uq_user_profiles_issuer_subject
  on user_profiles(auth_issuer, auth_subject);

commit;
