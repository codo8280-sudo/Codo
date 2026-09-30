# CODO - Déploiement technique de l'Increment 07

## Architecture cible

```text
Flutter Android/iOS
  -> HTTPS + OIDC Authorization Code / PKCE
Fournisseur OIDC
  -> JWT/JWKS
CODO API FastAPI 0.7
  -> PostgreSQL
  -> stockage persistant des originaux/extractions/brouillons
  -> embeddings optionnels
  -> LLM optionnel
```

Aucun secret serveur n'est compilé dans Flutter.

## 1. PostgreSQL et API

Depuis `backend/`, `compose.yaml` constitue une référence locale PostgreSQL + API. Fournir les secrets par environnement :

```text
export CODO_POSTGRES_PASSWORD='...'
export CODO_OIDC_ISSUER='https://identity.example/realms/codo'
export CODO_OIDC_AUDIENCE='codo-api'
docker compose up --build
```

Le conteneur lance `python -m scripts.migrate` avant FastAPI. La santé du conteneur utilise `/health/live`; la plateforme de déploiement doit utiliser `/health/ready` pour la readiness applicative.

## 2. Identité OIDC

Pour un environnement local isolé, `compose.identity-dev.yaml` fournit Keycloak et importe `keycloak/codo-realm.json`. Il n'est pas destiné à la production.

Le mobile utilise :

```text
CODO_OIDC_CLIENT_ID=codo-mobile
CODO_OIDC_REDIRECT_URL=ci.codo.app:/oauthredirect
```

Le backend exige une audience `codo-api`.

Avant staging partagé :

1. issuer HTTPS ;
2. audience API correcte ;
3. JWKS accessible ;
4. premier `SUPER_ADMIN` attribué dans `admin_memberships` ;
5. bootstrap token supprimé ;
6. `python -m scripts.staging_preflight` vert.

## 3. Flutter

Depuis la racine :

```text
./tool_bootstrap.sh
```

Le bootstrap :

- crée Android/iOS avec l'organisation `ci.codo` ;
- configure le callback AppAuth ;
- fixe Android API 24+ ;
- fixe iOS 13+ ;
- résout les dépendances ;
- exécute `flutter analyze`.

Build de staging, exemple :

```text
flutter run \
  --dart-define=CODO_API_BASE_URL=https://api.staging.example \
  --dart-define=CODO_OIDC_ISSUER=https://identity.staging.example/realms/codo \
  --dart-define=CODO_OIDC_CLIENT_ID=codo-mobile
```

Les valeurs OIDC du client public ne sont pas des secrets. Aucun client secret ne doit exister dans l'application native.

## 4. Pipeline documentaire

```text
source enregistrée
-> acquisition automatique OU binaire officiel fourni par documentaliste
-> original + SHA-256
-> snapshot de provenance
-> extraction
-> brouillon verification_pending
-> structuration
-> sources_verified
-> legal_review
-> décision juridique explicite
-> quality gate
-> validated
-> published
-> monitored
```

La voie `acquire-file` est une solution contrôlée pour les sites institutionnels qui bloquent l'acquisition machine. Elle est enregistrée `manual_review` et ne transforme jamais une déclaration d'URL en preuve de téléchargement automatique.

## 5. Premier corpus

Voir `FIRST_CORPUS_BOOTSTRAP.md`. Le document constitutionnel candidat reste non publié tant que l'original n'a pas été effectivement acquis dans l'environnement de staging et validé humainement.

## 6. Gate staging

Depuis `backend/` :

```text
python -m scripts.staging_preflight
python -m pytest -q
CODO_TEST_DATABASE_URL=postgresql://... python -m pytest -q -m integration
python -m scripts.e2e_staging --api-base https://api.staging.example
PYTHONPATH=backend python backend/scripts/staging_release.py --plan
```

## 7. Release gate audité

Pour une release staging complète :

```text
export CODO_DATABASE_URL='postgresql://...'
export CODO_E2E_USER_TOKEN='...'
export CODO_E2E_ADMIN_TOKEN='...'

PYTHONPATH=backend python backend/scripts/staging_release.py \
  --api-base https://api.staging.example \
  --document-id CODO-CI-CONST-2016 \
  --require-published-document
```

Le rapport est enregistré en JSON et, après migration 009, les checks sont aussi historisés en base.

## 8. Conditions de production publique

- PostgreSQL géré, sauvegardé et restauré en test ;
- stockage durable et versionné des originaux ;
- OIDC HTTPS de production ;
- TLS partout ;
- observabilité et alertes ;
- rotation des secrets ;
- suppression du bootstrap administratif ;
- tests d'intégration PostgreSQL ;
- premier corpus validé juridiquement ;
- procédure de retrait/correction d'un texte ;
- `flutter analyze`, tests et builds Android/iOS verts ;
- revue UI pixel-level contre le projet Stitch authentifié ;
- E2E mobile -> API -> PostgreSQL -> corpus -> provenance vert.

## Limitation de l'environnement de construction courant

Le conteneur utilisé pour produire cet Increment ne contient ni Docker, ni `psql`, ni Flutter/Dart et aucune URL PostgreSQL/OIDC de staging n'a été fournie. Le code et les gates sont prêts, mais un déploiement distant réel n'est donc pas présenté comme effectué.


## Supabase managed PostgreSQL

CODO may use a dedicated Supabase project as managed PostgreSQL. Do not point CODO at another product database. Configure `CODO_DATABASE_PROVIDER=supabase`, use a secure PostgreSQL connection string, run all migrations, then run `backend/scripts/supabase_preflight.py --json`. For long-lived backend containers prefer direct PostgreSQL connectivity when IPv6 is available; use the session pooler when the runtime is IPv4-only. See `docs/SUPABASE_STAGING.md`.
