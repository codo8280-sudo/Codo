# CODO - Increment 07 Summary

Date: 29 September 2026

## Objectif

Transformer la préparation staging de l'Increment 06 en une release reproductible, auditable et techniquement bloquante lorsqu'un prérequis juridique ou d'infrastructure manque.

## 1. Reçu cryptographique de publication

La migration `009_release_governance_and_publication_receipts.sql` ajoute `corpus_publication_receipts`.

Au moment exact de la transition `validated -> published`, CODO calcule un SHA-256 sur un payload canonique comprenant :

- identifiant CODO ;
- version ;
- statut juridique ;
- texte officiel du document ;
- articles ordonnés ;
- statuts des articles ;
- dates de validité ;
- hash du snapshot source.

Le reçu exige un validateur humain identifié et est inséré dans la même transaction que la publication. Une divergence ultérieure avec un reçu existant bloque l'opération.

Route publique :

```text
GET /v1/documents/{codo_id}/publication-receipt
```

Le mobile affiche désormais le hash de publication et le hash source sur la fiche article.

## 2. Quality gate rendu obligatoire

Les contrôles qualité ne sont plus seulement informatifs. Les transitions vers `validated` et `published` imposent désormais dans la transaction :

- original préservé ;
- source enregistrée et vérifiée ;
- métadonnées essentielles ;
- statut juridique final ;
- extraction conservée ;
- paquet structuré conservé ;
- articles structurés pour un texte normatif ;
- aucun article `verification_pending` ;
- provenance A/B suffisante correspondant au hash acquis.

Un appel direct à l'API ne peut donc plus contourner le rapport qualité.

## 3. Release gate staging

Nouveau script :

```text
backend/scripts/staging_release.py
```

Il orchestre :

1. migrations et checksums ;
2. bootstrap `SUPER_ADMIN` optionnel et explicite ;
3. preflight PostgreSQL/OIDC ;
4. E2E déployé ;
5. vérification du premier corpus publié si demandée ;
6. rapport JSON ;
7. audit SQL de la release.

Le mode `--plan` est sans effet de bord.

## 4. Gouvernance des releases

La migration 009 ajoute :

- `staging_release_runs` ;
- `staging_release_checks`.

Chaque gate peut donc être historisé au lieu d'être seulement visible dans les logs CI.

## 5. E2E renforcé

Le test staging vérifie maintenant aussi :

- le reçu de publication ;
- la longueur des hashes SHA-256 ;
- la chaîne document -> provenance -> receipt -> relations validées.

Les tokens E2E peuvent être fournis via `CODO_E2E_USER_TOKEN` et `CODO_E2E_ADMIN_TOKEN`, évitant de les exposer dans la ligne de commande.

## 6. CI fournisseur-indépendant

`tool_ci.sh` contrôle :

- syntaxe Python ;
- tests backend ;
- snapshot OpenAPI ;
- imports Dart relatifs ;
- Flutter format/analyze/tests lorsque le SDK est disponible.

## 7. API et versions

- API : **0.7.0** ;
- Flutter package : **0.7.0+7** ;
- OpenAPI : **36 chemins** ;
- migrations PostgreSQL : **9**.

## 8. Validation dans le conteneur

- tests Python : **51 passed** après ajout du quality gate et du reçu de publication ;
- test PostgreSQL réel : **1 skipped** faute de `CODO_TEST_DATABASE_URL` ;
- OpenAPI snapshot : cohérent ;
- imports Dart relatifs : aucun manquant sur 56 fichiers ;
- Flutter SDK : absent du conteneur, contrôles Flutter non revendiqués.

## 9. Ce qui reste réellement externe

Aucune base PostgreSQL/OIDC distante n'a été fournie. Increment 07 ne prétend donc pas avoir :

- provisionné un staging distant ;
- acquis le PDF constitutionnel depuis le réseau de staging ;
- simulé une validation juridique humaine ;
- publié le premier corpus réel ;
- produit un APK/IPA sans SDK Flutter.

Le projet est désormais équipé pour que ces opérations deviennent des gates exécutables et audités dès que l'infrastructure est fournie.
