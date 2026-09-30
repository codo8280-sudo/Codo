# CODO - Gouvernance du corpus juridique

## Règle centrale

Le corpus juridique est la source de vérité de CODO. Une réponse IA n'est jamais une source autonome.

`Question -> recherche documentaire -> résolution de version -> preuves -> réponse -> vérification des citations -> affichage`

## Niveaux de confiance

- **A** : source officielle primaire.
- **B** : reproduction institutionnelle.
- **C** : source secondaire vérifiée, complémentaire.
- **D** : source documentaire non vérifiée ; non exploitable pour établir une conclusion juridique.

Une conclusion juridique requiert au moins une source A ou B parmi les preuves retenues.

## Registre initial

Les migrations enregistrent notamment :

- Secrétariat Général du Gouvernement ;
- Journaux Officiels de Côte d'Ivoire ;
- Conseil constitutionnel ;
- Ministère de la Justice et des Droits de l'Homme ;
- OHADA ;
- Présidence de la République de Côte d'Ivoire pour le premier corpus constitutionnel candidat.

L'enregistrement d'une source ne publie aucune règle de droit.

## Provenance versionnée

CODO distingue :

- `legal_sources` : institution / source enregistrée ;
- `source_snapshots` : capture précise avec URL, hash, date, MIME et taille ;
- `legal_version_sources` : relation entre une version juridique et un snapshot ;
- `source_registry_checks` : contrôles successifs permettant de détecter un changement de contenu.

Rôles de provenance possibles :

- `primary_text` ;
- `amendment` ;
- `verification` ;
- `historical_reference`.

Une version publiée doit rester explicable par ses snapshots de provenance.

## Workflow obligatoire

`Importé -> À analyser -> Structuré -> Sources vérifiées -> Contrôle juridique -> Validé -> Publié -> Surveillé`

Étapes techniques intermédiaires :

- extraction ;
- génération de brouillon ;
- décision explicite du statut juridique ;
- contrôle qualité.

Aucune modification silencieuse d'un texte publié n'est autorisée.

## Brouillon automatique

L'extraction et le parseur peuvent aider à :

- détecter des articles ;
- proposer un découpage ;
- détecter des ruptures ou doublons ;
- produire des identifiants stables.

Ils ne peuvent pas :

- déclarer un texte en vigueur ;
- déduire seuls une date d'entrée en vigueur ;
- déclarer une abrogation ;
- publier ;
- remplacer une validation juridique.

Tout brouillon automatique utilise `verification_pending`.

## Publication d'une fiche

Contrôles bloquants :

1. original conservé ;
2. source enregistrée et vérifiée ;
3. provenance liée au hash acquis ;
4. structuration suffisante ;
5. aucun statut `verification_pending` ;
6. métadonnées principales présentes ;
7. extraction conservée ;
8. package structuré conservé ;
9. validation humaine enregistrée avant publication.

## Journal officiel

CODO doit distinguer consultation numérique, provenance institutionnelle et valeur probante de l'original. Une copie numérique utile à la recherche ne doit jamais être présentée comme ayant une valeur probante supérieure à celle indiquée par l'autorité compétente.

## IA

CODO IA n'obtient que des preuves publiées et vérifiées. Le modèle retourne des `evidence_id`; le serveur rejette tout identifiant absent de l'ensemble de preuves initialement fourni et revérifie la publication et la provenance avant de retourner les citations.
