# CODO - Staging Release Gate

Increment 07 introduit un gate de release exécutable et auditable.

## Objectif

Une release de staging ne doit être déclarée réussie que si :

1. toutes les migrations SQL s'appliquent et les checksums historiques restent intacts ;
2. le schéma attendu est présent ;
3. le stockage documentaire est inscriptible ;
4. l'issuer OIDC et ses JWKS sont accessibles ;
5. un `SUPER_ADMIN` actif existe ou qu'un mécanisme de récupération explicitement contrôlé reste disponible ;
6. l'API déployée répond aux contrôles E2E ;
7. lorsqu'un premier corpus publié est exigé, le document, sa provenance, son reçu de publication et son graphe public sont tous accessibles.

## Mode plan

Depuis la racine :

```text
PYTHONPATH=backend python backend/scripts/staging_release.py \
  --plan \
  --api-base https://api.staging.example \
  --document-id CODO-CI-CONST-2016 \
  --require-published-document
```

Ce mode ne modifie rien.

## Exécution

Les secrets restent uniquement dans les variables d'environnement :

```text
export CODO_DATABASE_URL='postgresql://...'
export CODO_OIDC_ISSUER='https://identity.staging.example/realms/codo'
export CODO_OIDC_AUDIENCE='codo-api'
export CODO_E2E_USER_TOKEN='...'
export CODO_E2E_ADMIN_TOKEN='...'

PYTHONPATH=backend python backend/scripts/staging_release.py \
  --api-base https://api.staging.example \
  --document-id CODO-CI-CONST-2016 \
  --require-published-document \
  --report staging-release-report.json
```

Pour le tout premier bootstrap uniquement, un sujet OIDC peut être explicitement promu `SUPER_ADMIN` :

```text
--bootstrap-super-admin-subject '<oidc-sub>'
```

Cette option n'est jamais implicite.

## Audit

Une fois la migration 009 appliquée, le gate enregistre :

- `staging_release_runs` ;
- `staging_release_checks`.

Le rapport JSON ne contient pas les tokens OIDC ni les credentials PostgreSQL. Les sorties sont nettoyées des motifs secrets courants avant écriture.

## Reçu de publication

Toute publication juridique crée de manière atomique un reçu dans `corpus_publication_receipts` contenant :

- identifiant CODO du document ;
- version ;
- hash SHA-256 du contenu juridique canonique publié ;
- hash SHA-256 de la source acquise ;
- identité interne du validateur ;
- identité interne du publieur ;
- date de publication.

L'API publique expose uniquement les informations nécessaires à la vérification technique : document, version, hashes et date. Les identités internes ne sont pas publiées.

## CI locale

```text
./tool_ci.sh
```

Le script exécute :

- compilation Python ;
- tests backend ;
- cohérence du snapshot OpenAPI ;
- contrôle des imports Dart relatifs ;
- contrôles Flutter si le SDK est installé.

`CODO_CI_REQUIRE_FLUTTER=true` rend l'absence de Flutter bloquante.


## Provider-specific gate

`staging_release.py` accepts `--provider postgres|supabase`. With `supabase`, a blocking provider-security check runs after the generic preflight. It verifies RLS, SSL and that no CODO table is granted to Supabase Data API roles.

Example:

```text
CODO_DATABASE_PROVIDER=supabase PYTHONPATH=backend python backend/scripts/staging_release.py --provider supabase --api-base https://staging-api.example
```
