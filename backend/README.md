# Backend CODO - Increment 08

API source-first indépendante du fournisseur d'hébergement.

## Capacités

### Public

- liveness/readiness ;
- recherche juridique ;
- documents, articles et historique ;
- provenance d'une version publiée ;
- reçu cryptographique de publication ;
- relations juridiques validées ;
- CODO IA avec evidence IDs contrôlés.

### Utilisateur OIDC

- `GET/PATCH/DELETE /v1/me` ;
- préférences d'accessibilité ;
- favoris ;
- dossiers et éléments de dossiers ;
- alertes/veille ;
- suppression de compte avec cascades des données personnelles dépendantes ;
- aucun access token n'est persisté côté serveur.

### Administration

- OIDC Bearer + RBAC CODO local ;
- gestion des habilitations ;
- acquisition automatique institutionnelle ;
- acquisition de binaire officiel fournie par un documentaliste (`manual_review`) ;
- extraction PDF ;
- brouillon `verification_pending` ;
- structuration ;
- décision juridique ;
- contrôle qualité ;
- validation/publication ;
- candidats de relations juridiques et validation humaine.

## Sécurité d'identité

Le même issuer OIDC peut authentifier citoyens et administrateurs. Un token valide ne donne jamais de rôle administratif à lui seul : les permissions proviennent exclusivement de `admin_memberships`.

Les profils citoyens sont identifiés par la paire `(auth_issuer, auth_subject)`, car un `sub` OIDC n'est unique qu'au sein de son issuer. La migration 008 corrige ce modèle sans modifier les migrations historiques.

Lors d'une suppression de compte, CODO ne conserve pas l'identifiant OIDC. Le registre de confidentialité reçoit uniquement un digest SHA-256 non corrélable utilisant un nonce aléatoire non stocké.

## Migrations PostgreSQL

Appliquer dans l'ordre via `python -m scripts.migrate` :

```text
001_initial_schema.sql
002_mvp_features.sql
003_seed_official_sources.sql
004_retrieval_and_acquisition.sql
005_first_corpus_and_provenance.sql
006_oidc_rbac_and_relationship_candidates.sql
007_user_oidc_and_privacy.sql
008_oidc_subject_namespace.sql
009_release_governance_and_publication_receipts.sql
010_provider_security_hardening.sql
```

Le runner stocke le SHA-256 de chaque migration dans `codo_schema_migrations`. Toute altération ultérieure d'un fichier déjà appliqué arrête le déploiement.

## Workflow juridique

```text
acquisition
-> imported
-> extraction
-> to_analyze
-> draft verification_pending
-> structured
-> sources_verified
-> legal_review
-> explicit legal decision
-> quality gate
-> validated
-> published
-> monitored
```

Aucune transition de validation ne peut contourner le statut `verification_pending`, la provenance, le quality gate bloquant ou la revue humaine.

## Acquisition documentaire

### Automatique

`POST /v1/admin/ingestion/acquire`

Le serveur vérifie domaine enregistré, redirections, MIME, taille, conserve l'original, calcule SHA-256, crée le snapshot et journalise `reachable`, `changed` ou `unchanged`.

### Binaire officiel fourni par un opérateur

`POST /v1/admin/ingestion/acquire-file`

Cette voie existe uniquement lorsque l'acquisition serveur est bloquée par la source officielle. L'opérateur doit être authentifié et fournir une URL appartenant à un domaine institutionnel enregistré. Le serveur vérifie aussi la signature `%PDF-` pour un PDF. Le contrôle est enregistré comme `manual_review` : CODO ne prétend jamais que le binaire a été téléchargé automatiquement depuis cette URL.

## Reçu de publication

La transition `validated -> published` crée atomiquement un reçu SHA-256 dans `corpus_publication_receipts`. Le reçu public expose la version, le hash du contenu publié, le hash source et la date, sans exposer les identités internes des validateurs.

## Recherche et IA

La recherche plein texte PostgreSQL reste le socle. pgvector et un fournisseur d'embeddings sont optionnels. CODO IA n'utilise que des preuves issues de versions publiées et vérifiées ; tout evidence ID inventé ou substitué est rejeté.

## OIDC local de développement

Le fichier `compose.identity-dev.yaml` lance un Keycloak de référence et importe `keycloak/codo-realm.json`. Il est réservé au développement/test local.

```text
export CODO_KEYCLOAK_ADMIN='...'
export CODO_KEYCLOAK_ADMIN_PASSWORD='...'
docker compose -f compose.identity-dev.yaml up
```

Pour staging/production, utiliser un fournisseur OIDC exposé en HTTPS et configurer :

```text
CODO_OIDC_ISSUER=https://identity.example/realms/codo
CODO_OIDC_AUDIENCE=codo-api
```

## Gate de staging

Depuis `backend/` :

```text
python -m scripts.staging_preflight
python -m scripts.e2e_staging --api-base https://api.staging.example
python -m scripts.staging_release --plan
```

Le préflight vérifie notamment toutes les migrations attendues, l'index d'unicité `(issuer, subject)`, le stockage, OIDC/JWKS et la récupération administrative.

## Secrets

Ne jamais intégrer dans Flutter :

- mot de passe PostgreSQL ;
- bootstrap token ;
- clé LLM ;
- clé embeddings ;
- `STITCH_API_KEY` ;
- secret d'un client OIDC confidentiel.

Le client mobile `codo-mobile` est public et utilise PKCE sans client secret.


## Provider security preflight

For a dedicated Supabase staging database:

```text
CODO_DATABASE_PROVIDER=supabase
PYTHONPATH=backend python scripts/supabase_preflight.py --json
```

The check requires SSL, RLS on every CODO table and zero Data API grants for `anon`, `authenticated` and `service_role`.
