# CODO - Premier corpus juridique candidat

Date de préparation : 29 septembre 2026

## Objet

Le premier corpus candidat est la Constitution de la République de Côte d'Ivoire issue de la loi n° 2016-886 du 8 novembre 2016, dans sa présentation consolidée indiquant les révisions constitutionnelles n° 2020-348 du 19 mars 2020 et n° 2023-693 du 25 juillet 2023.

Cette fiche prépare l'ingestion mais **ne publie aucun texte juridique**. Le contenu ne devient consultable par le public qu'après acquisition de l'original, contrôle de provenance, structuration, décision de statut juridique, validation humaine et publication.

## Source primaire candidate

- Registre CODO : `CI-PRESIDENCE`
- Institution : Présidence de la République de Côte d'Ivoire
- URL du document candidat : `https://www.presidence.ci/wp-content/uploads/2025/06/Constitution-livret-ok.pdf`
- Manifeste : `backend/manifests/ci_constitution_2016_consolidated_2023.json`

## Sources institutionnelles de vérification

- Conseil constitutionnel - page « La Constitution » : `https://www.conseil-constitutionnel.ci/lois-et-decrets/la-constitution`
- Conseil constitutionnel - décision relative au contrôle de la révision 2023 : `https://www.conseil-constitutionnel.ci/sites/default/files/decision_2023.007_du_04.08.2023.pdf`

Ces références servent à la vérification institutionnelle. Elles ne remplacent pas l'acquisition du document principal ni la validation juridique humaine.

## Chaîne d'ingestion

```text
Source enregistrée
-> acquisition réseau
-> original conservé
-> SHA-256
-> source_snapshot
-> extraction PDF
-> brouillon structuré verification_pending
-> contrôle des diagnostics
-> structuration
-> provenance liée à la version
-> sources_verified
-> legal_review
-> décision explicite du statut juridique
-> contrôle qualité
-> validated
-> published
-> chunks lexicaux
-> monitored
```

## Script d'amorçage sécurisé

Depuis la racine du projet, après déploiement de l'API et de PostgreSQL :

```text
python backend/scripts/bootstrap_first_corpus.py \
  --api-base https://votre-api-codo.example \
  --admin-token '<token-de-preproduction>'
```

Le script s'arrête volontairement après la génération du brouillon. Il ne structure, ne valide et ne publie rien automatiquement.

## Contrôles bloquants avant validation

- original conservé ;
- source institutionnelle enregistrée et vérifiée ;
- snapshot de provenance lié au hash acquis ;
- articles structurés pour les textes normatifs ;
- aucun statut `verification_pending` ;
- titre et version présents ;
- trace d'extraction conservée ;
- paquet structuré conservé.

## Règle de prudence

La date de mise en ligne d'un PDF, le nom d'un fichier ou la date d'impression d'un livret ne sont jamais utilisés seuls pour déduire une date d'entrée en vigueur. Toute date d'effet doit être confirmée par une source juridique appropriée avant validation.


## Increment 05 relationship candidates

The 2020 and 2023 constitutional amendment links are stored first as relationship candidates from `backend/manifests/ci_constitution_relationship_candidates.json`. Loading the manifest does not publish a graph edge.

```text
python backend/scripts/bootstrap_relationship_candidates.py
```

A legal-review role must approve each candidate after both legal documents have been ingested. Only then is a row created in `legal_relationships` and exposed by the public graph endpoint.

## Increment 06 - acquisition manuelle contrôlée

Si le serveur de l'institution refuse l'acquisition machine mais qu'un documentaliste dispose du **binaire officiel** obtenu depuis la source institutionnelle, l'API permet une voie de secours authentifiée :

```text
POST /v1/admin/ingestion/acquire-file?source_key=CI-PRESIDENCE&source_url=<url-officielle>
Content-Type: application/pdf
Authorization: Bearer <token-documentaliste>
<body binaire PDF>
```

Cette voie :

- exige un rôle d'ingestion autorisé ;
- exige une URL appartenant au domaine institutionnel enregistré ;
- contrôle la taille et le type du binaire ;
- contrôle la signature `%PDF-` pour un PDF ;
- conserve l'original ;
- calcule SHA-256 ;
- crée le snapshot et l'audit ;
- marque le contrôle `manual_review`.

Le statut `manual_review` est volontaire : CODO n'affirme pas que le serveur a lui-même récupéré le binaire depuis l'URL déclarée. La revue documentaire et juridique reste obligatoire.
