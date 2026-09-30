# CODO

**Centre d'Orientation du Droit et des Obligations**

CODO est une plateforme source-first d'information, de compréhension et d'orientation juridique pour le droit applicable en Côte d'Ivoire.

## Increment 08 - état courant

Cette arborescence est cumulative : elle inclut les travaux des Increments 01 à 07 et les ajouts de l'Increment 08.

### Stack

- Flutter Android/iOS ;
- API Python/FastAPI 0.8 ;
- PostgreSQL ;
- recherche plein texte PostgreSQL ;
- pgvector optionnel ;
- OIDC Authorization Code + PKCE côté mobile ;
- validation JWT/JWKS côté API ;
- fournisseurs embeddings/LLM optionnels et exclusivement côté serveur ;
- contrat REST dans `backend/openapi.yaml`.

## Principe non négociable

```text
Situation utilisateur
-> corpus vérifié
-> version juridiquement qualifiée
-> provenance et hash
-> source officielle/institutionnelle
-> explication/orientation
-> citations vérifiées
```

Aucun article ou délai juridique fictif n'est utilisé pour remplir l'interface.

## Mobile

Le client conserve la famille des 35 écrans du design maître et ajoute désormais :

- connexion OIDC native Authorization Code + PKCE ;
- stockage sécurisé des access/refresh/ID tokens ;
- renouvellement automatique de session ;
- profil utilisateur synchronisé ;
- préférences d'accessibilité synchronisées ;
- favoris synchronisés ;
- dossiers documentaires synchronisés ;
- alertes/veille synchronisées ;
- suppression de compte en libre-service ;
- sauvegarde d'un article depuis la fiche article ;
- affichage de la provenance, des relations juridiques validées et du reçu cryptographique de publication.

Sans `CODO_API_BASE_URL` ou sans configuration OIDC, le client reste en mode sûr et ne fabrique aucun résultat juridique.

### Bootstrap Flutter

```text
./tool_bootstrap.sh
```

Le script crée les projets natifs avec l'organisation `ci.codo`, configure le callback `ci.codo.app:/oauthredirect`, Android API 24+ et iOS 13+, puis lance `flutter pub get` et `flutter analyze`.

## Backend

Voir notamment :

- `backend/README.md` ;
- `backend/openapi.yaml` ;
- `docs/DEPLOYMENT.md` ;
- `docs/OIDC_SECURITY.md` ;
- `docs/MOBILE_OIDC.md` ;
- `docs/STAGING_E2E.md` ;
- `docs/POSTGRES_STAGING_ACCEPTANCE.md` ;
- `docs/RELEASE_GATE.md` ;
- `docs/LEGAL_DATA_GOVERNANCE.md` ;
- `docs/FIRST_CORPUS_BOOTSTRAP.md`.

### Migrations

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

Les migrations appliquées sont enregistrées avec leur SHA-256. Une migration historique modifiée bloque le déploiement ; toute évolution passe par un nouveau numéro.

## Développement API

Depuis `backend/` :

```text
python -m venv .venv
pip install -r requirements.txt
python -m scripts.migrate
uvicorn app.main:app --reload
```

## Identité locale de référence

`backend/compose.identity-dev.yaml` fournit un Keycloak de développement avec import du realm CODO. Aucun mot de passe ou utilisateur de test n'est commité.

## Premier corpus candidat

Le premier corpus préparé reste la Constitution ivoirienne consolidée identifiant les modifications de 2020 et 2023. Le bootstrap s'arrête volontairement au brouillon et n'effectue jamais de publication automatique.

Si le serveur institutionnel refuse une acquisition machine, un documentaliste authentifié peut fournir le binaire officiel à la route `acquire-file`. CODO contrôle le domaine déclaré, le type de contenu, la signature PDF, conserve le binaire et son SHA-256, mais marque cette acquisition `manual_review` au lieu de prétendre l'avoir téléchargée automatiquement.

## Release gate staging

Le gate cumulatif de staging s'exécute via :

```text
PYTHONPATH=backend python backend/scripts/staging_release.py --plan
./tool_ci.sh
```

En exécution réelle, le gate applique les migrations, vérifie PostgreSQL/OIDC, lance les E2E et produit un rapport JSON audité.


## Provider-aware staging

CODO remains compatible with standard PostgreSQL and now supports an explicit Supabase staging profile. `CODO_DATABASE_PROVIDER=supabase` enables an additional blocking preflight that verifies RLS, SSL and closure of Data API grants. See `docs/SUPABASE_STAGING.md`.

Remote CI definitions are available under `.github/workflows/`; see `docs/REMOTE_CI.md`.

## Validation actuelle

Voir `BUILD_STATUS.md` et `docs/INCREMENT_08_SUMMARY.md`.

`STITCH_API_KEY` reste une variable d'outillage. Elle ne doit jamais être compilée dans l'application ou copiée dans le backend public.
