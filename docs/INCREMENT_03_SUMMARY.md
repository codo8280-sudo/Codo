# CODO — Increment 03 Summary

Date : 29 septembre 2026

## Périmètre réalisé

### Backend exécutable

- API FastAPI 0.3 structurée par routers/services/repositories/providers ;
- endpoint `/health` ;
- recherche publique source-first ;
- lecture document/article/historique ;
- CODO IA avec retrieval avant génération ;
- validation indépendante des citations ;
- refus explicite lorsque les sources ne suffisent pas ;
- quatre niveaux de réponse : simple, détaillé, juridique, professionnel.

### Recherche hybride

- recherche plein texte PostgreSQL ;
- table de chunks ;
- pgvector optionnel ;
- adaptateur embeddings compatible endpoint HTTP ;
- fusion lexical/sémantique par RRF ;
- fallback automatique vers le lexical.

### Ingestion documentaire

- acquisition limitée aux domaines officiels enregistrés ;
- redirections contrôlées ;
- limites de taille ;
- conservation de l'original ;
- empreinte SHA-256 ;
- snapshots ;
- artifacts ;
- structuration liée au hash source ;
- interdiction de réécrire une version déjà publiée ;
- protection des identifiants CODO stables.

### Workflow juridique

Transitions strictes :

```text
imported -> to_analyze -> structured -> sources_verified
-> legal_review -> validated -> published -> monitored
```

Publication atomique des versions courantes, reviews et audit.

### Flutter

- support des quatre niveaux CODO IA ;
- affichage du niveau de confiance d'une citation ;
- indication textuelle du type de recherche lexical/sémantique/hybride ;
- gestion plus robuste des erreurs FastAPI.

### Déploiement

- Dockerfile Python ;
- compose PostgreSQL 18 + pgvector + API ;
- migration runner ;
- volumes persistants ;
- healthchecks ;
- modèle de variables d'environnement ;
- guide `docs/DEPLOYMENT.md`.

## Contrôles exécutés

- compilation syntaxique Python : OK ;
- 14 tests unitaires de politique documentaire/workflow : OK ;
- TestClient FastAPI racine et health : OK ;
- refus contrôlé des routes corpus sans base : OK ;
- OpenAPI 3.1 YAML : OK ;
- aucun SDK Flutter/Dart disponible dans ce conteneur ;
- aucun serveur PostgreSQL local disponible dans ce conteneur ;
- tests d'intégration PostgreSQL et build Flutter restent donc à exécuter dans l'environnement de déploiement.

## État de sécurité juridique

Aucun article de loi fictif, délai fictif, jurisprudence fictive ou conclusion juridique simulée n'a été ajouté.

Le registre de sources existant reste la provenance initiale ; la présence d'une source dans le registre n'entraîne pas la publication automatique d'un contenu.

## Étape suivante

1. connecter une base PostgreSQL réelle ;
2. appliquer les migrations ;
3. acquérir un premier corpus officiel autorisé ;
4. structurer et valider humainement ce corpus ;
5. construire les chunks ;
6. brancher embeddings/LLM si retenus ;
7. exécuter tests d'intégration et Flutter ;
8. remplacer l'authentification bootstrap admin par OIDC/roles.
