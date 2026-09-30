# CODO
## Centre d’Orientation du Droit et des Obligations

**Cahier des spécifications fonctionnelles et techniques — Version initiale**  
**Territoire initial : République de Côte d’Ivoire**  
**Date de référence : 29 septembre 2026**

---

# 1. Définition du produit

**CODO est une plateforme numérique nationale d’accès, de recherche, de compréhension et d’orientation dans le droit applicable en Côte d’Ivoire.**

Sa finalité est simple :

> **Permettre à toute personne de trouver la règle de droit qui concerne sa situation, de la comprendre et de savoir quelles démarches entreprendre.**

CODO ne doit donc pas être seulement une bibliothèque de PDF.

La plateforme doit relier cinq éléments :

**Situation de l’utilisateur → Droit applicable → Source juridique → Explication → Procédure à suivre**

CODO devient ainsi une **centrale numérique du droit et des procédures**.

---

# 2. Principes fondamentaux

## 2.1. Primauté des sources

CODO doit systématiquement distinguer :

- le texte juridique original ;
- les métadonnées du texte ;
- les explications produites par CODO ;
- les réponses générées par l’intelligence artificielle ;
- les commentaires éventuels de professionnels.

Le Secrétariat général du Gouvernement indique que seule la version originale du Journal officiel disponible dans ses locaux a valeur probante. CODO devra donc afficher clairement le niveau d’autorité et de vérification de chaque document numérique.

Le SGG assure notamment la publication au Journal officiel des actes législatifs et réglementaires autorisés à la publication.

---

# 3. Doctrine CODO : aucune règle sans source

Une réponse CODO ne doit jamais simplement annoncer :

> « La loi dit que… »

Elle devra permettre à l’utilisateur de voir immédiatement :

**Source**  
**Texte**  
**Numéro**  
**Article**  
**Version**  
**Date**  
**Statut juridique**  
**Lien vers le document source**

Exemple :

> Selon l’article X de la loi n° XXXX-XXX du XX/XX/XXXX…

Puis :

**Consulter l’article original**

Cette exigence doit être inscrite dans l’architecture même de l’application.

---

# 4. Gestion du statut des textes

Chaque texte devra recevoir un statut visible.

### Statuts principaux

- **En vigueur**
- **Partiellement en vigueur**
- **Modifié**
- **Abrogé**
- **Remplacé**
- **Suspendu**, lorsqu’un fondement officiel permet de l’établir
- **Projet de loi**
- **Projet de décret**
- **Texte adopté en attente de publication/promulgation**, selon le cas
- **Version historique**
- **Statut en cours de vérification**

Cette distinction est indispensable.

Ainsi, le Conseil des ministres du 23 septembre 2026 a annoncé l’adoption d’un **projet de loi** modifiant le Code pénal. CODO ne devra jamais présenter une telle annonce comme si les modifications étaient déjà nécessairement entrées dans le droit positif applicable.

---

# 5. Sources documentaires prioritaires

CODO devra construire un registre officiel de sources.

## Niveau A — Sources institutionnelles prioritaires

### Secrétariat général du Gouvernement
Pour le Journal officiel, les lois, ordonnances, décrets et autres publications gouvernementales.

### Conseil constitutionnel
Pour la Constitution et les décisions ou documents publiés par l’institution.

Le Conseil constitutionnel met notamment à disposition différentes versions historiques de la Constitution.

### Ministère de la Justice et des Droits de l’Homme
Pour les textes juridiques, informations judiciaires, formulaires, procédures, cartographies juridictionnelles et documentation relevant de son domaine. Le portail du ministère comporte notamment des rubriques « Textes juridiques », « Formulaires et procédures », « Décisions de justice » et « Cartographie judiciaire ».

### OHADA
Une partie majeure du droit des affaires applicable en Côte d’Ivoire relève également des Actes uniformes OHADA.

Le corpus officiel OHADA couvre notamment le droit commercial général, les sociétés commerciales et GIE, les sûretés, les procédures collectives, le recouvrement et les voies d’exécution, l’arbitrage, la médiation, la comptabilité, les sociétés coopératives et certains transports.

CODO devra donc éviter l’erreur consistant à présenter le droit commercial ivoirien uniquement comme un « Code de commerce » national.

---

# 6. Architecture fonctionnelle générale

La plateforme sera organisée autour de **10 grands moteurs**.

## M01 — CODO Recherche

Moteur universel permettant de rechercher :

- Constitution ;
- codes ;
- lois ;
- ordonnances ;
- décrets ;
- arrêtés ;
- règlements ;
- Actes uniformes OHADA ;
- jurisprudence disponible ;
- procédures ;
- institutions ;
- formulaires ;
- articles de loi ;
- définitions juridiques.

La recherche accepte aussi des questions naturelles.

Exemples :

> « Quel est le délai pour contester un licenciement ? »

> « Mon bailleur veut me faire sortir de la maison. »

> « Comment porter plainte ? »

> « Comment récupérer une dette ? »

> « Est-ce que je peux construire sur mon terrain ? »

---

# 7. M02 — Bibliothèque juridique

La bibliothèque constitue le cœur documentaire de CODO.

L’utilisateur pourra naviguer par :

**Domaine → Corpus → Texte → Livre → Titre → Chapitre → Section → Article**

Exemple :

**Droit pénal → Code pénal → Livre → Titre → Article**

Chaque article disposera d’une page propre.

---

# 8. Fiche d’un article

Une fiche article devra contenir au minimum :

### Article X

**Texte officiel**

Contenu exact de l’article.

**État**

En vigueur / modifié / abrogé.

**Applicable depuis**

Date juridiquement vérifiée.

**Texte d’origine**

Référence de la loi, ordonnance ou autre acte.

**Dernière modification**

Référence correspondante.

**Version antérieure**

Accessible depuis l’historique.

**Explication CODO**

Explication en langage accessible.

**À retenir**

Résumé très court.

**Situations concernées**

Exemples pratiques.

**Articles associés**

Liens automatiques.

**Procédures associées**

Lorsque pertinent.

**Source officielle**

Document et provenance.

---

# 9. M03 — CODO IA

CODO disposera d’un assistant juridique conversationnel spécialisé dans le droit applicable en Côte d’Ivoire.

Il ne devra pas fonctionner comme un chatbot généraliste répondant de mémoire.

Son architecture devra être fondée sur :

**Question → Compréhension → Recherche documentaire → Sélection des sources → Analyse → Réponse → Citations**

La réponse ne devra être générée qu’après consultation du corpus CODO pertinent.

---

# 10. Structure obligatoire d’une réponse CODO IA

Pour une question juridique, le format standard sera :

### Votre situation

Reformulation factuelle, sans modifier les faits communiqués.

### Ce que prévoit le droit

Explication synthétique.

### Textes applicables

Articles, lois ou autres textes.

### Ce que vous pouvez faire

Étapes ou options juridiquement documentées.

### Documents susceptibles d’être nécessaires

Liste adaptée à la procédure.

### Où effectuer la démarche

Institution ou juridiction lorsque celle-ci peut être déterminée.

### Délais

Uniquement lorsqu’ils sont établis par une source fiable.

### Points nécessitant une attention particulière

Exceptions, conditions ou incertitudes.

### Sources

Accès aux documents originaux.

---

# 11. Interdiction des hallucinations juridiques

CODO IA devra respecter plusieurs règles techniques obligatoires.

L’IA ne doit pas :

- inventer un article ;
- inventer un numéro de loi ;
- inventer une jurisprudence ;
- inventer une juridiction ;
- inventer un délai ;
- présenter un projet comme un texte applicable ;
- utiliser une disposition abrogée comme droit actuel sans avertissement ;
- masquer une incertitude documentaire.

Lorsque CODO ne possède pas de source suffisamment fiable, il devra répondre explicitement :

> **« CODO ne dispose pas actuellement d’une source vérifiée suffisante pour confirmer ce point. »**

---

# 12. Modes de réponse

CODO IA proposera plusieurs niveaux.

### Simple

Explication destinée au grand public.

### Détaillé

Explication avec règles, exceptions et procédure.

### Juridique

Articles et références approfondies.

### Professionnel

Recherche documentaire avancée destinée notamment aux juristes.

Le fondement juridique restera identique ; seule la profondeur d’explication changera.

---

# 13. M04 — CODO Procédures

Il s’agit de l’un des modules les plus importants.

CODO doit transformer les procédures complexes en parcours.

Exemple :

## Porter plainte

**1. Comprendre la situation**

↓

**2. Identifier la nature possible des faits**

↓

**3. Préparer les informations et documents**

↓

**4. Identifier l’autorité susceptible d’être compétente**

↓

**5. Effectuer la démarche**

↓

**6. Comprendre les étapes suivantes**

↓

**7. Identifier les recours éventuels**

Chaque étape est reliée aux sources correspondantes.

---

# 14. Domaines procéduraux

CODO devra progressivement couvrir notamment :

- dépôt de plainte ;
- procédure pénale ;
- garde à vue ;
- convocation ;
- instruction ;
- jugement ;
- recours ;
- recouvrement de créances ;
- litiges locatifs ;
- conflits fonciers ;
- succession ;
- divorce ;
- état civil ;
- droit du travail ;
- licenciement ;
- accident du travail ;
- création et fonctionnement des entreprises ;
- contentieux commerciaux ;
- construction ;
- urbanisme ;
- fiscalité ;
- contentieux administratif ;
- marchés publics ;
- consommation ;
- assurances ;
- transport ;
- accidents de circulation.

---

# 15. M05 — CODO Situations de vie

Beaucoup d’utilisateurs ne connaissent pas la branche juridique correspondant à leur problème.

Ils pourront donc entrer par une situation.

### Travail
« J’ai été licencié »

### Famille
« Je veux divorcer »

### Logement
« Mon propriétaire veut augmenter mon loyer »

### Terrain
« Deux personnes revendiquent la même parcelle »

### Police / Justice
« J’ai reçu une convocation »

### Entreprise
« Un client refuse de payer »

### Construction
« Je veux construire une maison »

### Route
« J’ai eu un accident »

### Internet
« Quelqu’un utilise mes photos sans autorisation »

CODO traduit ensuite la situation en domaines juridiques et recherche les sources correspondantes.

---

# 16. M06 — CODO Jurisprudence

Le système devra progressivement indexer les décisions de justice accessibles légalement.

Chaque décision pourra être structurée selon :

**Juridiction**  
**Formation**  
**Date**  
**Numéro**  
**Matière**  
**Textes cités**  
**Faits**  
**Question juridique**  
**Décision**  
**Source**

Pour les matières OHADA, l’écosystème officiel publie notamment de la jurisprudence de la CCJA.

L’IA devra toujours différencier :

**Texte normatif** ≠ **décision juridictionnelle** ≠ **commentaire ou doctrine**

---

# 17. M07 — Annuaire juridique et institutionnel

CODO contiendra progressivement un annuaire de :

- tribunaux ;
- cours d’appel ;
- juridictions compétentes ;
- administrations ;
- ministères ;
- services publics ;
- greffes ;
- organisations professionnelles ;
- structures publiques utiles.

Pour chaque structure :

**Nom**  
**Type**  
**Compétences documentées**  
**Adresse**  
**Contacts publics**  
**Horaires lorsqu’ils sont officiellement disponibles**  
**Site officiel**  
**Procédures réalisables**

---

# 18. M08 — Mon espace CODO

Création de compte facultative pour les recherches ordinaires.

L’espace personnel permettra de :

- enregistrer des textes ;
- enregistrer des articles ;
- conserver des recherches ;
- créer des dossiers ;
- suivre une matière juridique ;
- recevoir des alertes réglementaires ;
- conserver des procédures favorites.

Les informations personnelles sensibles devront être strictement séparées du corpus juridique.

---

# 19. Veille juridique

L’utilisateur pourra suivre :

**Code pénal**

**Droit du travail**

**Fiscalité**

**Construction**

**Droit commercial**

etc.

Lorsqu’une modification juridiquement vérifiée intervient :

> **« Le texte que vous suivez a été modifié. »**

L’utilisateur pourra consulter :

**ancienne version ↔ nouvelle version**

avec les articles concernés.

---

# 20. M09 — CODO Pro

Interface destinée aux utilisateurs avancés :

- juristes ;
- avocats ;
- étudiants ;
- chercheurs ;
- entreprises ;
- directions juridiques ;
- administrations.

Fonctions envisagées :

- recherche booléenne ;
- recherche multicritère ;
- comparaison de textes ;
- recherche par période ;
- recherche par référence ;
- dossiers documentaires ;
- export de références ;
- historique législatif ;
- veille spécialisée.

---

# 21. M10 — Administration CODO

Un back-office complet est obligatoire.

Il ne doit jamais être nécessaire de modifier le code informatique pour publier une nouvelle loi.

Le back-office permettra de gérer :

- domaines juridiques ;
- sources ;
- textes ;
- articles ;
- versions ;
- relations entre textes ;
- jurisprudence ;
- procédures ;
- institutions ;
- actualités juridiques ;
- contrôles de qualité ;
- alertes ;
- indexation IA.

---

# 22. Workflow éditorial

Une publication juridique devra suivre un processus contrôlé :

**Importé**

→ **À analyser**

→ **Structuré**

→ **Sources vérifiées**

→ **Contrôle juridique**

→ **Validé**

→ **Publié**

→ **Surveillé**

Aucune modification silencieuse d’un texte publié ne sera admise.

Chaque modification devra être historisée.

---

# 23. Rôles d’administration

### SUPER_ADMIN
Administration générale du système.

### RESPONSABLE_JURIDIQUE
Supervision du corpus.

### VALIDATEUR_JURIDIQUE
Validation des textes et métadonnées.

### DOCUMENTALISTE
Importation et structuration.

### REDACTEUR
Création des explications simplifiées et procédures.

### DATA_MANAGER
Gestion et qualité des données.

### MODERATEUR
Supervision des contenus utilisateurs.

### AUDITEUR
Consultation des historiques et journaux sans capacité de modification.

---

# 24. Modèle de données principal

La base CODO comportera notamment :

### legal_sources
Sources institutionnelles.

### legal_domains
Branches du droit.

### legal_documents
Lois, décrets, codes, ordonnances, Actes uniformes, etc.

### legal_document_versions
Versions successives.

### legal_articles
Articles individualisés.

### legal_article_versions
Historique article par article.

### amendments
Modifications.

### repeals
Abrogations.

### legal_relationships
Liens entre textes.

### jurisdictions
Juridictions.

### institutions
Institutions publiques.

### case_law
Jurisprudence.

### procedures
Procédures.

### procedure_steps
Étapes.

### required_documents
Documents associés.

### legal_topics
Thématiques.

### practical_situations
Situations de vie.

### citations
Références utilisées par les réponses.

### ai_answers
Réponses produites, lorsque leur conservation est autorisée.

### source_snapshots
Copies de contrôle permettant de vérifier quelle version d’une source a été utilisée.

### legal_reviews
Validations humaines.

### audit_logs
Historique complet des opérations d’administration.

---

# 25. Identité unique d’un texte

Chaque texte recevra un identifiant interne stable.

Exemple :

`CODO-CI-LOI-2019-574`

Les articles auront également leur identifiant.

Exemple :

`CODO-CI-LOI-2019-574-ART-001`

Cela permettra de gérer correctement les évolutions sans casser les liens historiques.

---

# 26. Architecture de recherche

CODO utilisera une recherche hybride combinant :

### Recherche exacte
Numéro, article, date, intitulé.

### Recherche plein texte
Termes juridiques.

### Recherche sémantique
Sens de la question.

### Recherche structurée
Domaine, période, institution, statut.

### Recherche conversationnelle
Question naturelle à CODO IA.

L’intelligence artificielle ne doit donc jamais remplacer le moteur documentaire : **elle doit l’exploiter**.

---

# 27. Architecture IA

Architecture cible :

**Interface CODO**

↓

**API CODO**

↓

**Orchestrateur juridique**

↓

**Analyse de la question**

↓

**Recherche hybride**

↓

**Corpus juridique CODO**

↓

**Contrôle des versions**

↓

**Sélection des passages pertinents**

↓

**LLM**

↓

**Vérification des citations**

↓

**Réponse à l’utilisateur**

Cette approche de type RAG permettra de limiter fortement les réponses non documentées.

---

# 28. Niveau de confiance documentaire

Chaque source recevra un niveau interne de confiance.

### A — Source officielle primaire

Document émis ou publié par l’institution compétente.

### B — Reproduction institutionnelle

Copie disponible sur une autre plateforme publique fiable.

### C — Source secondaire vérifiée

Publication spécialisée ou universitaire utilisée à titre complémentaire.

### D — Source documentaire non vérifiée

Non exploitable pour produire une conclusion juridique tant qu’une validation n’a pas eu lieu.

Le niveau D pourra servir à identifier un document à rechercher, mais pas à établir seul une réponse juridique.

---

# 29. Design de l’interface

CODO doit éviter une esthétique intimidante de cabinet juridique.

L'interface devra être :

**sobre, moderne, rassurante, extrêmement lisible et mobile-first.**

La page d’accueil pourra être organisée autour d’une question centrale :

> **Que souhaitez-vous comprendre aujourd’hui ?**

avec une grande zone :

**Posez votre question à CODO**

Puis :

**Rechercher une loi**

**Comprendre une procédure**

**Explorer mes droits**

**Consulter les codes**

**Trouver une juridiction**

---

# 30. Navigation principale

### Accueil

### Demander à CODO

### Lois & Codes

### Procédures

### Mes droits

### Jurisprudence

### Institutions

### Actualité juridique

### Mon espace

---

# 31. Accessibilité

CODO devra pouvoir être utilisé aussi par une personne qui maîtrise difficilement le vocabulaire juridique.

Fonctions à prévoir :

- explication simple ;
- lecture audio ;
- commande vocale ;
- recherche vocale ;
- taille de caractères réglable ;
- contraste renforcé ;
- navigation accessible ;
- mode faible connexion ;
- mise en cache des textes importants.

À terme, certains contenus pédagogiques pourront être adaptés aux principales langues utilisées en Côte d’Ivoire, tout en conservant le français du texte juridique original comme référence lorsque celui-ci est la langue du texte officiel.

---

# 32. Application mobile

CODO devra être disponible sous plusieurs formes :

**Web responsive**

**PWA**

**Android**

**iOS**

L’utilisateur mobile pourra notamment :

- poser une question oralement ;
- scanner éventuellement la référence d’un document ;
- télécharger certains textes pour consultation hors connexion ;
- écouter une explication ;
- recevoir des alertes juridiques.

---

# 33. Protection des utilisateurs

Des sujets sensibles peuvent être soumis à CODO :

- infractions ;
- violences ;
- conflits familiaux ;
- arrestations ;
- dossiers professionnels ;
- données d’entreprise ;
- situations judiciaires.

La plateforme devra appliquer une politique stricte de minimisation des données.

L’utilisateur ne devra pas être obligé de fournir son identité pour consulter la loi.

Les conversations sensibles ne devront pas devenir automatiquement des données d’entraînement.

---

# 34. Information juridique et représentation professionnelle

CODO pourra :

- informer ;
- rechercher ;
- citer ;
- expliquer ;
- orienter ;
- structurer une procédure ;
- indiquer les sources.

Mais lorsqu’une situation requiert un conseil individualisé important, une représentation ou un acte relevant d’un professionnel habilité, CODO devra l’indiquer clairement.

Une évolution ultérieure pourra proposer un **réseau de professionnels vérifiés**, sans compromettre l’indépendance des réponses documentaires.

---

# 35. Domaines de lancement

La première version opérationnelle ne doit pas attendre que l’ensemble du droit ivoirien soit numérisé.

## Lot 1

### Constitution

La Constitution constitue le point d’entrée institutionnel naturel. Le Conseil constitutionnel publie son corpus constitutionnel.

### Droit pénal

### Procédure pénale

### Droit du travail

### Foncier / immobilier

### Construction / urbanisme

### Famille

### Droit commercial et OHADA

Les textes officiels OHADA devront être directement intégrés dans le dispositif documentaire pour les matières concernées.

### Recouvrement des créances

### Procédures judiciaires essentielles

---

# 36. Version MVP

La première version exploitable de CODO comprendra :

1. portail public ;
2. moteur de recherche juridique ;
3. bibliothèque ;
4. fiches textes ;
5. fiches articles ;
6. moteur de versionnement ;
7. CODO IA ;
8. citations obligatoires ;
9. procédures essentielles ;
10. situations de vie ;
11. authentification facultative ;
12. favoris ;
13. veille ;
14. back-office ;
15. workflow juridique ;
16. journal d’audit.

---

# 37. Phase 2

Ajout de :

- jurisprudence avancée ;
- annuaire juridictionnel ;
- comparateur juridique ;
- CODO Pro ;
- dossiers professionnels ;
- alertes personnalisées ;
- recherche vocale ;
- lecture audio ;
- applications mobiles complètes.

---

# 38. Phase 3

Évolutions envisageables :

- assistant procédural avancé ;
- génération guidée de documents administratifs simples ;
- formulaires interactifs ;
- parcours judiciaires cartographiés ;
- plateforme API juridique ;
- intégration institutionnelle ;
- observatoire de l’évolution normative ;
- analyse comparative de versions ;
- statistiques anonymisées sur les difficultés d’accès au droit.

---

# 39. Architecture technique recommandée

## Front-end Web

**Next.js + TypeScript**

## Mobile

**Flutter**

## Base transactionnelle

**PostgreSQL**

## Authentification

Architecture compatible avec :

- compte classique ;
- OTP ;
- fournisseurs d’identité futurs.

## Stockage documentaire

Stockage objet compatible S3.

## Recherche

PostgreSQL Full Text Search en première étape, complété si nécessaire par un moteur spécialisé.

## Recherche sémantique

`pgvector` ou service vectoriel équivalent.

## IA

Architecture multi-modèles afin de ne pas rendre CODO dépendant d’un seul fournisseur.

## API

REST et, si nécessaire, services spécialisés internes.

---

# 40. Services internes

Architecture modulaire recommandée :

`identity-service`

`legal-corpus-service`

`legal-search-service`

`legal-versioning-service`

`procedure-service`

`jurisprudence-service`

`institution-service`

`ai-orchestrator`

`citation-verifier`

`ingestion-service`

`notification-service`

`audit-service`

`admin-service`

---

# 41. Pipeline documentaire

Lorsqu’un nouveau texte apparaît :

**Détection**

↓

**Acquisition**

↓

**Conservation du document original**

↓

**Extraction**

↓

**Identification**

↓

**Structuration**

↓

**Découpage en articles**

↓

**Détection des références**

↓

**Comparaison avec le corpus existant**

↓

**Contrôle humain**

↓

**Validation juridique**

↓

**Publication**

↓

**Indexation**

↓

**Indexation sémantique**

↓

**Notification éventuelle aux utilisateurs**

---

# 42. Versionnement juridique

CODO doit pouvoir répondre à deux questions différentes :

> « Que dit la loi aujourd’hui ? »

et :

> « Que disait la loi le 15 janvier 2022 ? »

Il faut donc un versionnement temporel complet.

Aucune ancienne disposition ne doit être détruite après une modification.

---

# 43. Relations juridiques

CODO constituera progressivement un **graphe du droit ivoirien**.

Exemple :

**Loi A**

→ modifie → **Loi B**

→ abroge → **Article C**

→ applique → **Disposition D**

→ est complétée par → **Décret E**

→ citée par → **Décision F**

Cette architecture deviendra un avantage majeur de la plateforme.

---

# 44. CODO Graph

À terme, l’utilisateur pourra voir visuellement :

**Texte d’origine**

↓

**Modifications**

↓

**Décrets d’application**

↓

**Articles liés**

↓

**Jurisprudence**

↓

**Procédures**

↓

**Institutions concernées**

Cela permettra de passer d’une simple bibliothèque à une véritable **cartographie intelligente du droit**.

---

# 45. Contrôle qualité

Avant toute mise en production, un article juridique devra notamment passer les contrôles suivants :

**Source identifiée ?**

**Document original conservé ?**

**Numéro vérifié ?**

**Date vérifiée ?**

**Version vérifiée ?**

**Statut vérifié ?**

**Texte complet ?**

**Relations de modification vérifiées ?**

**Citations IA testées ?**

**Historique enregistré ?**

---

# 46. Critères de lancement

CODO ne devra être considéré comme prêt pour son lancement public que lorsque :

- aucune réponse juridique n’est fournie sans source lorsque la réponse repose sur le corpus ;
- les versions des textes sont traçables ;
- les articles peuvent être cités individuellement ;
- un texte abrogé ou historique est clairement identifié ;
- les projets sont distingués des textes applicables ;
- les modifications sont historisées ;
- le moteur de recherche retrouve les articles précis ;
- l’IA sait reconnaître l’absence de source suffisante ;
- le back-office permet une validation humaine ;
- les opérations d’administration sont auditées.

---

# 47. Proposition de valeur définitive

CODO ne sera pas :

**une collection de PDF.**

CODO sera :

> **une infrastructure numérique permettant de rechercher, comprendre, relier et suivre le droit applicable en Côte d’Ivoire.**

L’objectif final est qu’une personne puisse passer de :

**« J’ai un problème »**

à :

**« Je comprends ce que prévoit le droit »**

puis :

**« Je connais le texte qui le prévoit »**

puis :

**« Je sais quelles démarches sont prévues »**

puis :

**« Je sais à quelle institution m’adresser. »**

---

# 48. Identité officielle

**Nom : CODO**

**Développement : Centre d’Orientation du Droit et des Obligations**

**Catégorie : LegalTech / GovTech / information et orientation juridique**

**Pays de lancement : Côte d’Ivoire**

**Mission : rendre le droit accessible, compréhensible, traçable et exploitable par tous.**

**Vision : devenir la porte d’entrée numérique de référence vers le droit applicable en Côte d’Ivoire.**

**Signature principale :**

# CODO — Le droit ivoirien, accessible à tous.

**Principe fondateur :**

> **Une question. Une règle. Une source. Une orientation.**