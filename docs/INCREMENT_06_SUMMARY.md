# CODO - Increment 06 Summary

Date: 29 September 2026

## Objectif

Faire passer CODO d'un backend OIDC/RBAC principalement administratif à une chaîne d'exploitation comprenant aussi l'identité citoyenne mobile, la synchronisation des données personnelles minimales, le stockage sécurisé des tokens, une acquisition documentaire de secours contrôlée et un véritable gate staging externe.

## 1. Identité citoyenne

L'API distingue désormais :

- `UserPrincipal` : utilisateur OIDC authentifié ;
- `AdminPrincipal` : utilisateur OIDC disposant en plus de rôles actifs dans `admin_memberships`.

Un token valide n'accorde jamais de pouvoir administratif par lui-même.

Endpoints utilisateur :

```text
GET    /v1/me
PATCH  /v1/me
DELETE /v1/me
GET    /v1/me/accessibility
PUT    /v1/me/accessibility
GET    /v1/me/favorites
POST   /v1/me/favorites
DELETE /v1/me/favorites/{id}
GET    /v1/me/folders
POST   /v1/me/folders
GET    /v1/me/folders/{id}/items
POST   /v1/me/folders/{id}/items
DELETE /v1/me/folders/{id}/items/{itemId}
DELETE /v1/me/folders/{id}
GET    /v1/me/alerts
POST   /v1/me/alerts
PATCH  /v1/me/alerts/{id}
DELETE /v1/me/alerts/{id}
```

## 2. Correction du namespace OIDC

La migration 007 avait ajouté `auth_issuer` aux profils historiques, mais la contrainte héritée restait une unicité de `auth_subject` seul. Increment 06 ajoute la migration **008**, sans réécrire l'historique :

```text
unique(auth_issuer, auth_subject)
```

Le service d'upsert utilise désormais exactement cette paire.

## 3. Confidentialité et suppression

`DELETE /v1/me` supprime le profil et ses données dépendantes via les cascades prévues. Le registre de confidentialité ne conserve pas le `sub` OIDC : il stocke un digest SHA-256 calculé avec un nonce cryptographique frais non conservé, rendant l'événement non corrélable au sujet supprimé.

## 4. Flutter OIDC

Le mobile utilise Authorization Code + PKCE :

- découverte OIDC ;
- `flutter_appauth` ;
- `flutter_secure_storage` ;
- stockage sécurisé access/refresh/ID tokens ;
- refresh automatique ;
- end-session ;
- aucune valeur de client secret.

Le bootstrap natif configure le callback `ci.codo.app:/oauthredirect`, Android API 24+ et iOS 13+.

## 5. Espace personnel réel

Les écrans Connexion, Mon espace, Favoris, Dossiers, Alertes/veille et Accessibilité utilisent désormais l'API lorsqu'un compte OIDC est connecté. La fiche article peut ajouter un article aux favoris. Les dossiers et abonnements de veille sont toujours filtrés par le `user_id` du profil authentifié.

## 6. Acquisition documentaire opérateur

Nouvelle route :

```text
POST /v1/admin/ingestion/acquire-file
```

Elle répond au cas où un serveur institutionnel bloque l'acquisition machine mais où un documentaliste possède le binaire officiel. La route exige authentification/autorisation, domaine enregistré, taille/MIME valides et signature PDF. Le résultat est conservé et haché, mais le contrôle porte le statut `manual_review`.

Cette voie ne réduit aucune des étapes : extraction, structuration, source verification, legal review, quality gate et publication restent obligatoires.

## 7. Readiness et staging

Ajouts :

- `/health/live` ;
- `/health/ready` ;
- Keycloak de développement importable ;
- realm CODO sans compte de démonstration ;
- script `scripts/e2e_staging.py` non destructif ;
- préflight amélioré : tables, migrations attendues, index d'identité, stockage, JWKS, récupération SUPER_ADMIN.

## 8. API

Le contrat OpenAPI 3.1 régénéré expose **35 chemins** et le schéma `HTTPBearer`.

## 9. Tests

Résultat courant :

```text
42 passed, 1 skipped
```

Le test ignoré est l'intégration PostgreSQL réelle car aucun `CODO_TEST_DATABASE_URL` n'est disponible dans cet environnement.

## 10. Limites réelles de l'environnement

L'environnement de construction ne fournit pas :

- PostgreSQL/psql ;
- Docker ;
- Flutter/Dart ;
- URL ou credentials d'un staging CODO ;
- fournisseur OIDC de staging déjà déployé.

Aucun déploiement externe, build mobile ou publication juridique n'est donc affirmé sans preuve.

## 11. Prochaine tranche

Une fois un staging réellement disponible, Increment 07 devra être orienté vers l'exécution plutôt que l'ajout de couches : migrations réelles, bootstrap SUPER_ADMIN, première acquisition officielle, revue et publication contrôlée, E2E complet et CI Flutter.
