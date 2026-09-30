# PostgreSQL Staging Acceptance - Increment 06

## But

Une base non vérifiée ne doit jamais servir à publier le corpus juridique CODO.

## Politique de migration

`python -m scripts.migrate` crée `codo_schema_migrations` et enregistre le SHA-256 de chaque migration appliquée.

Règles :

- une migration historique appliquée est immuable ;
- un checksum différent arrête le déploiement ;
- toute évolution utilise un nouveau fichier numéroté ;
- le préflight exige que toutes les migrations présentes dans `postgres/` soient enregistrées et qu'aucune migration inconnue ne soit déclarée dans la base.

Migrations actuelles :

1. `001_initial_schema.sql`
2. `002_mvp_features.sql`
3. `003_seed_official_sources.sql`
4. `004_retrieval_and_acquisition.sql`
5. `005_first_corpus_and_provenance.sql`
6. `006_oidc_rbac_and_relationship_candidates.sql`
7. `007_user_oidc_and_privacy.sql`
8. `008_oidc_subject_namespace.sql`
9. `009_release_governance_and_publication_receipts.sql`

## Modèle OIDC utilisateur

La paire `(auth_issuer, auth_subject)` doit être unique. Le préflight vérifie l'existence de `uq_user_profiles_issuer_subject`.

## Test d'intégration PostgreSQL

Configurer une base jetable :

```text
CODO_TEST_DATABASE_URL=postgresql://...
```

Puis depuis `backend/` :

```text
python -m pytest -q -m integration
```

Le test d'intégration est volontairement ignoré lorsqu'aucune base de test n'est fournie.

## Preflight staging

Depuis `backend/` :

```text
python -m scripts.staging_preflight
```

Le gate contrôle :

- connexion PostgreSQL ;
- tables critiques ;
- migrations et checksums ;
- namespace OIDC des profils ;
- stockage persistant et inscriptible ;
- découverte OIDC et JWKS ;
- au moins un `SUPER_ADMIN` actif ou un mécanisme bootstrap temporaire de récupération.

Un code de sortie non nul bloque l'acceptation staging.

## E2E déployé

Après preflight :

```text
python -m scripts.e2e_staging \
  --api-base https://api.staging.example \
  --user-token "$CODO_E2E_USER_TOKEN" \
  --admin-token "$CODO_E2E_ADMIN_TOKEN" \
  --document-id CODO-CI-CONST-2016
```

Le script vérifie liveness, readiness, recherche publique, identité citoyenne, rôles d'administration, document publié, provenance SHA-256 et relations publiques validées. Il n'effectue aucune mutation juridique.

## Conditions avant publication d'un premier texte

- sauvegarde PostgreSQL créée ;
- restauration réellement testée dans un environnement séparé ;
- stockage des originaux sauvegardé ;
- OIDC accessible en HTTPS ;
- bootstrap token retiré après création du premier `SUPER_ADMIN` ;
- corpus acquis et haché ;
- source A/B vérifiée ;
- revue juridique humaine ;
- statut explicite sans `verification_pending` ;
- contrôle qualité vert ;
- E2E staging vert.


## Supabase profile acceptance

When `CODO_DATABASE_PROVIDER=supabase`, staging additionally requires:

- SSL active on the PostgreSQL session;
- Supabase roles `anon`, `authenticated`, `service_role` present;
- RLS enabled on all CODO tables;
- zero table grants to those Data API roles;
- migration 010 applied and checksum-verified.
