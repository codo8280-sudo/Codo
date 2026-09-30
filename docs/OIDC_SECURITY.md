# CODO OIDC Security Model - Increment 06

## Principe

Le fournisseur OpenID Connect prouve l'identité. Il ne décide jamais des rôles juridiques ou administratifs CODO.

CODO distingue deux niveaux :

1. **UserPrincipal** - tout utilisateur OIDC authentifié peut accéder à son espace personnel ;
2. **AdminPrincipal** - le même utilisateur doit en plus posséder un rôle actif dans `admin_memberships` pour accéder au back-office.

## Configuration serveur

Configuration générique :

```text
CODO_OIDC_ISSUER=https://identity.example/realms/codo
CODO_OIDC_AUDIENCE=codo-api
CODO_OIDC_ALGORITHMS=RS256
```

Configuration vérifiée de `Codo_Staging` :

```text
CODO_OIDC_ISSUER=https://evchtqxpthfaekpaeibh.supabase.co/auth/v1
CODO_OIDC_AUDIENCE=authenticated
CODO_OIDC_ALGORITHMS=ES256
```

Le document de discovery staging annonce `RS256`, `HS256` et `ES256`, mais le JWKS actif expose actuellement une clé de signature `EC/ES256`. CODO limite donc volontairement le staging à `ES256` au lieu d'accepter tous les algorithmes annoncés.

L'API contrôle :

- signature contre JWKS ;
- allowlist d'algorithmes ;
- `iss` ;
- `aud` ;
- `exp` ;
- `iat` ;
- présence d'un `sub` non vide.

Discovery et JWKS exigent HTTPS. `CODO_OIDC_ALLOW_INSECURE_HTTP=true` est réservé à un développement local isolé.

## Mobile

Le client `codo-mobile` est un client public :

- Authorization Code Flow ;
- PKCE ;
- aucun client secret ;
- callback `ci.codo.app:/oauthredirect` ;
- access/refresh/ID tokens dans le secure storage de la plateforme ;
- refresh token utilisé uniquement depuis l'appareil ;
- access token transmis à l'API dans `Authorization: Bearer ...`.

## Namespace d'identité

Un OIDC `sub` n'est unique qu'au sein d'un issuer. Les profils citoyens utilisent donc la clé logique :

```text
(auth_issuer, auth_subject)
```

La migration `008_oidc_subject_namespace.sql` impose cette unicité.

## Autorisation administrative locale

Après validation du JWT, les rôles actifs sont résolus depuis PostgreSQL. Les claims de rôles du fournisseur ne sont jamais convertis automatiquement en rôles CODO.

Rôles :

- SUPER_ADMIN
- RESPONSABLE_JURIDIQUE
- VALIDATEUR_JURIDIQUE
- DOCUMENTALISTE
- REDACTEUR
- DATA_MANAGER
- MODERATEUR
- AUDITEUR

## Bootstrap recovery

`CODO_ADMIN_BOOTSTRAP_TOKEN` sert uniquement au bootstrap/récupération.

Séquence recommandée :

1. déployer PostgreSQL et l'API ;
2. appliquer les migrations ;
3. configurer OIDC ;
4. identifier le premier sujet OIDC de confiance ;
5. attribuer `SUPER_ADMIN` avec le script dédié ;
6. vérifier `GET /v1/admin/me` ;
7. retirer le bootstrap token de l'environnement partagé/production.

Sans bootstrap recovery, CODO protège le dernier `SUPER_ADMIN` actif contre une révocation accidentelle.

## Suppression d'un compte citoyen

La suppression libre-service efface le profil et les données personnelles dépendantes. Un événement minimal de suppression est conservé sans `sub`, sans e-mail et sans issuer exploitable. Son digest inclut un nonce cryptographique frais non stocké, ce qui empêche de recalculer ou corréler l'identité supprimée depuis le registre.

## Keycloak de développement

`backend/compose.identity-dev.yaml` et `backend/keycloak/codo-realm.json` servent uniquement de référence locale. Aucun compte ni mot de passe de démonstration n'est commité.

## Gate opérationnel

Depuis `backend/` :

```text
python -m scripts.staging_preflight
```

Le préflight contrôle la base, toutes les migrations, l'unicité `(issuer, subject)`, le stockage, le mécanisme de récupération `SUPER_ADMIN`, la discovery OIDC et JWKS.
