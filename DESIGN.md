# Design System: CODO

**Produit :** CODO — Centre d’Orientation du Droit et des Obligations  
**Territoire initial :** Côte d’Ivoire  
**Catégorie :** LegalTech / information juridique / orientation procédurale  
**Signature :** Le droit ivoirien, accessible à tous.

---

# 1. Visual Theme & Atmosphere

CODO doit inspirer immédiatement quatre perceptions :

**fiabilité, clarté, accessibilité et autorité.**

L’interface ne doit toutefois jamais ressembler à un ancien portail administratif ni à un cabinet d’avocats traditionnel.

L’identité visuelle doit évoquer une **institution numérique contemporaine**, capable d’accueillir aussi bien :

- un citoyen qui cherche simplement à comprendre ses droits ;
- un étudiant ;
- un entrepreneur ;
- un salarié ;
- un propriétaire ou locataire ;
- un professionnel du droit ;
- une entreprise ;
- une administration.

## Atmosphère

**Institutionnelle sans être froide.**  
**Premium sans être luxueuse.**  
**Technologique sans paraître futuriste.**  
**Accessible sans devenir simpliste.**  
**Sérieuse sans devenir intimidante.**

### Réglages de personnalité

- **Density : 5/10 — Daily App Balanced**
- **Variance : 6/10 — Controlled Asymmetry**
- **Motion : 4/10 — Restrained Fluidity**

L’utilisateur doit ressentir qu’il consulte une plateforme de confiance et non un chatbot générique.

---

# 2. Design Philosophy

Le principe central est :

> **La source juridique doit toujours être plus importante visuellement que l’intelligence artificielle.**

L’IA accompagne.

Le droit constitue la référence.

L’interface doit constamment distinguer :

**Texte officiel**

**Explication CODO**

**Orientation pratique**

**Réponse IA**

**Source**

**Version**

**Statut juridique**

Cette séparation doit être comprise immédiatement, même par une personne sans formation juridique.

---

# 3. Color Palette & Roles

CODO utilise une palette extrêmement contrôlée.

Une seule couleur d’accent est autorisée.

## Ivory Canvas — #F8F8F5

Fond principal de l’application.

Légèrement chaleureux afin d’éviter la froideur clinique du blanc pur.

Utilisation :

- pages publiques ;
- espaces de lecture ;
- arrière-plans principaux ;
- grands espaces de respiration.

---

## Pure Surface — #FFFFFF

Surface de premier niveau.

Utilisation :

- champs de recherche ;
- panneaux ;
- fiches juridiques ;
- fenêtres ;
- surfaces élevées.

---

## Legal Ink — #181A1B

Couleur principale du texte.

Jamais utiliser #000000.

Utilisation :

- titres ;
- corps des textes juridiques ;
- navigation ;
- informations essentielles.

---

## Secondary Graphite — #62676C

Texte secondaire.

Utilisation :

- explications ;
- métadonnées ;
- dates ;
- références secondaires ;
- descriptions.

---

## Quiet Border — #E5E6E2

Bordure structurelle discrète.

Utilisation :

- séparateurs ;
- champs ;
- tableaux ;
- éléments documentaires ;
- panneaux.

---

## Soft Surface — #F0F1ED

Surface secondaire.

Utilisation :

- filtres ;
- blocs d’explication ;
- éléments inactifs ;
- fonds documentaires.

---

## CODO Civic Green — #197052

**Unique couleur d’accent de toute l’application.**

Elle représente :

- action ;
- validation ;
- navigation active ;
- confiance ;
- source vérifiée ;
- CTA principal ;
- focus.

Ne jamais utiliser plusieurs couleurs vives pour différencier artificiellement les sections.

Les statuts doivent s’appuyer prioritairement sur :

- texte ;
- icône ;
- niveau de contraste ;
- contour ;
- structure.

La couleur ne doit jamais être le seul vecteur d’information.

---

# 4. Typography

## Display Font

**Geist**

Utilisation :

- H1 ;
- H2 ;
- grands chiffres ;
- intitulés principaux ;
- titres d’écrans.

Caractéristiques :

- tracking légèrement serré ;
- très forte lisibilité ;
- autorité moderne ;
- absence d’effet décoratif inutile.

---

## Body Font

**Geist**

Utilisation :

- contenu courant ;
- réponses IA ;
- explications ;
- formulaires ;
- navigation.

Le corps principal doit conserver une largeur maximale d’environ **65 caractères par ligne** pour les contenus longs.

---

## Legal / Metadata Font

**Geist Mono**

Utilisation limitée à :

- numéros de lois ;
- références ;
- numéros d’articles ;
- dates légales ;
- identifiants CODO ;
- versionnement ;
- journaux techniques.

Exemple :

`LOI N° 2019-574`

`ARTICLE 183`

---

# 5. Typography Scale

## Hero

Desktop :

`clamp(3rem, 5vw, 5.25rem)`

Mobile :

minimum environ `2.5rem`

Line-height serré mais confortable.

---

## H1

`clamp(2rem, 3vw, 3.5rem)`

---

## H2

`clamp(1.5rem, 2vw, 2.25rem)`

---

## H3

`1.25rem – 1.5rem`

---

## Body Large

`1.125rem`

Line-height environ `1.7`

---

## Body

`1rem`

Line-height environ `1.65`

---

## Metadata

`0.875rem`

---

# 6. Logo Direction

Le logo CODO doit être essentiellement typographique.

Le mot :

# CODO

doit être immédiatement reconnaissable.

Une piste identitaire intéressante consiste à transformer subtilement l’un des deux « O » en symbole évoquant :

- une ouverture ;
- un document ;
- un portail ;
- un cercle de connaissance ;
- un repère.

Le logo ne doit pas utiliser :

- marteau de juge cliché ;
- balance de justice générique ;
- colonne grecque ;
- perruque juridique ;
- parchemin ancien.

CODO représente **le droit contemporain accessible**, pas l’imagerie juridique historique.

---

# 7. Layout Architecture

## Desktop container

Largeur maximale :

**1440 px**

La plupart des contenus :

**1180–1280 px**

Lecture juridique :

**760–860 px**

---

## Grid

Desktop :

12 colonnes.

Tablet :

8 colonnes.

Mobile :

4 colonnes.

---

# 8. Spacing System

Unité de base :

**4 px**

Espacements recommandés :

4  
8  
12  
16  
24  
32  
40  
48  
64  
80  
96  
128

Les pages documentaires doivent privilégier l’espace blanc plutôt que les bordures excessives.

---

# 9. Border Radius

L’interface ne doit pas être excessivement arrondie.

### Champs

12–16 px

### Boutons

12–14 px

### Petits éléments

8–10 px

### Panneaux importants

20–24 px

### Grandes compositions éditoriales

jusqu’à 28 px.

Éviter systématiquement les cartes « bulle » de 32–40 px partout.

---

# 10. Shadows

Les ombres sont très discrètes.

Aucun glow.

Aucune ombre noire lourde.

Les surfaces importantes utilisent éventuellement :

- bordure légère ;
- petit contraste de fond ;
- ombre très diffuse.

L’information juridique doit paraître stable et non flottante.

---

# 11. Buttons

## Primary

Fond :

**CODO Civic Green #197052**

Texte :

blanc.

Hauteur minimum :

48 px.

État actif :

translation verticale de 1 px maximum.

Pas de glow.

---

## Secondary

Surface blanche ou transparente.

Contour Quiet Border.

Texte Legal Ink.

---

## Ghost

Sans fond.

Pour actions secondaires :

- copier ;
- imprimer ;
- sauvegarder ;
- partager ;
- comparer.

---

# 12. Inputs

Tous les formulaires respectent :

**Label au-dessus**

**Champ**

**Texte d’aide éventuel**

**Erreur en dessous**

Pas de label flottant.

Hauteur cible :

48–56 px.

Focus :

contour Civic Green clairement visible.

---

# 13. Universal Search

La recherche constitue le composant central de CODO.

Elle doit pouvoir accepter :

- question ;
- loi ;
- numéro ;
- article ;
- procédure ;
- situation courante.

Exemple de placeholder :

**Recherchez une loi, un article, une procédure ou posez votre question**

Le champ doit supporter :

- texte ;
- voix ;
- historique ;
- suggestions ;
- recherche récente.

---

# 14. Homepage Hero

Le Hero n’est jamais centré.

Structure asymétrique.

## Zone gauche

Petit marqueur :

**Centre d’Orientation du Droit et des Obligations**

Grand titre :

**Comprendre le droit.  
Savoir comment agir.**

Une petite illustration contextuelle ou miniature documentaire peut être intégrée dans la composition typographique sans jamais chevaucher les mots.

Sous-titre :

**Recherchez les textes applicables en Côte d’Ivoire, comprenez vos droits et accédez aux procédures correspondantes.**

CTA unique :

**Poser une question à CODO**

---

## Zone droite

Composition documentaire contemporaine :

- extrait d’article ;
- numéro de loi ;
- statut ;
- source ;
- mini parcours procédural.

Pas de grande illustration générique de personnes serrant la main.

---

# 15. Homepage Structure

Après le Hero :

## Recherche universelle

Grande surface dédiée.

---

## « Que voulez-vous faire ? »

Organisation asymétrique.

Pas trois cartes identiques.

Utiliser plutôt :

Grande entrée :

**Comprendre une situation**

Puis modules plus petits :

**Consulter les lois**

**Suivre une procédure**

**Trouver une institution**

**Explorer vos droits**

---

## Domaines juridiques

Navigation éditoriale en grille irrégulière ou liste structurée.

Exemples :

Droit pénal  
Travail  
Famille  
Immobilier  
Construction  
Entreprises  
OHADA  
Fiscalité  
Numérique  
Consommation

---

## Dernières évolutions juridiques

Format chronologique.

Chaque entrée affiche :

- nature ;
- date ;
- texte ;
- statut ;
- source.

---

# 16. CODO AI Screen

CODO IA ne doit pas visuellement ressembler à un clone de ChatGPT.

## Desktop

Disposition deux zones.

### Colonne principale

Conversation.

### Panneau contextuel

Sources utilisées.

Le panneau sources doit rester accessible pendant la lecture.

---

## Réponse CODO

Chaque réponse est divisée en blocs sémantiques :

### Votre situation

### Ce que prévoit le droit

### Ce que vous pouvez faire

### Procédure

### Textes applicables

### Sources

Les citations doivent être visibles directement dans le texte.

---

# 17. Legal Source Component

Chaque source dispose d’un composant standard :

**LOI**

`N° XXXX-XXX`

Titre du texte

`Article XX`

Statut :

**En vigueur**

Version :

**mise à jour du …**

Institution :

…

Bouton :

**Voir le texte officiel**

La provenance documentaire doit être immédiatement identifiable.

---

# 18. Reliability Indicator

Ne pas utiliser un score arbitraire comme :

« 98 % fiable ».

Afficher plutôt :

**Source officielle vérifiée**

ou

**Source institutionnelle**

ou

**Statut à vérifier**

avec une explication accessible.

---

# 19. Laws & Codes Explorer

Desktop :

navigation à trois zones.

### Gauche

Corpus.

### Centre

Structure du texte.

### Droite

Contenu de l’article ou informations contextuelles.

Sur mobile :

navigation séquentielle.

Aucun défilement horizontal.

---

# 20. Article Page

L’article de loi est traité comme un contenu de lecture premium.

Header :

**CODE PÉNAL**

**Article 123**

Badge discret :

**En vigueur**

Puis texte officiel.

Le texte officiel doit être visuellement clairement séparé de :

### Comprendre cet article

Explication CODO.

### Situations concernées

Exemples.

### Textes liés

Relations juridiques.

### Historique

Versions.

### Source originale

Accès au document.

---

# 21. Procedure Screen

Les procédures doivent être particulièrement pédagogiques.

Utiliser une timeline verticale.

Exemple :

01 — Vérifier les conditions

02 — Réunir les documents

03 — Saisir l’autorité compétente

04 — Effectuer la démarche

05 — Suivre le dossier

06 — Exercer un recours si applicable

L’étape active utilise Civic Green.

Les autres utilisent les neutres.

---

# 22. Life Situations Screen

Titre :

**Que vous arrive-t-il ?**

Grand champ de recherche.

Puis catégories contextualisées :

**Travail**

« Mon employeur ne me paie plus »

**Logement**

« Mon propriétaire veut me faire quitter le logement »

**Famille**

« Je souhaite divorcer »

**Entreprise**

« Un client refuse de payer »

**Justice**

« J’ai reçu une convocation »

L’utilisateur raisonne par situation, pas nécessairement par branche juridique.

---

# 23. Jurisprudence

Interface plus dense.

Chaque décision affiche :

- juridiction ;
- date ;
- numéro ;
- matière ;
- question juridique ;
- textes cités.

Utiliser Geist Mono pour références.

Filtres persistants sur desktop.

Filtres dans un drawer sur mobile.

---

# 24. Institutions Screen

Recherche :

**Trouver une juridiction ou une administration**

Chaque institution :

Nom

Type

Compétences

Adresse officielle

Contacts vérifiés

Site officiel

Démarches proposées.

Un système cartographique pourra être ajouté ultérieurement.

---

# 25. User Space

Navigation :

**Vue d’ensemble**

**Mes textes**

**Mes procédures**

**Mes recherches**

**Mes alertes**

**Mes dossiers**

L’interface reste documentaire plutôt que « dashboard SaaS ».

Éviter les KPI artificiels.

---

# 26. Legal Monitoring

Écran :

# Ma veille juridique

Timeline.

Exemple :

**Code pénal**

Modification détectée

23 septembre 2026

Statut documentaire

Articles concernés

CTA :

**Comparer les versions**

---

# 27. Text Comparison

Vue desktop double colonne.

### Version précédente

### Version actuelle

Modifications mises en évidence sans palette multicolore excessive.

Utiliser :

- fond neutre ;
- barré ;
- souligné ;
- Civic Green uniquement pour information active.

Mobile :

versions empilées.

---

# 28. CODO Pro

Interface plus dense.

Recherche avancée en tête.

Filtres :

- nature ;
- numéro ;
- date ;
- domaine ;
- statut ;
- institution ;
- juridiction ;
- texte cité.

Résultats sous forme documentaire.

Pas de cartes décoratives.

---

# 29. Admin Legal Workspace

Le back-office est conçu comme un véritable poste de travail documentaire.

Desktop prioritaire.

Navigation latérale :

**Tableau de bord**

**Corpus**

**Textes**

**Articles**

**Imports**

**Modifications**

**Procédures**

**Jurisprudence**

**Institutions**

**Validation**

**Sources**

**Utilisateurs**

**Audit**

---

# 30. Admin Review Screen

Disposition trois zones.

### Gauche

Document source.

### Centre

Contenu structuré.

### Droite

Métadonnées et validation.

Actions principales :

**Valider**

**Demander correction**

**Rejeter**

**Publier**

Chaque action sensible doit être historisée.

---

# 31. Status Language

Le statut doit être visible sous forme de petite capsule sémantique.

Exemples :

**En vigueur**

**Modifié**

**Abrogé**

**Projet de loi**

**Historique**

**En vérification**

Pas de badges multicolores façon outil de gestion de projet.

---

# 32. Mobile Navigation

Barre basse :

**Accueil**

**Recherche**

**CODO**

**Procédures**

**Espace**

Maximum cinq entrées.

Les fonctions secondaires sont placées dans le menu.

---

# 33. Responsive Rules

Sous 768 px :

toutes les compositions multi-colonnes deviennent verticales.

Aucun défilement horizontal.

Touch target minimum :

**44 × 44 px**

Les titres utilisent `clamp()`.

Les documents restent parfaitement lisibles.

Les panneaux latéraux deviennent :

- drawer ;
- sheet ;
- accordéon ;
- écrans dédiés.

---

# 34. Loading States

Aucun spinner générique au centre de la page.

Utiliser des skeletons qui reproduisent précisément :

- ligne de texte ;
- titre ;
- source ;
- résultat ;
- article.

---

# 35. Empty States

Ne jamais afficher simplement :

**Aucune donnée**

Exemple :

### Aucun texte enregistré

**Enregistrez un article ou une loi pour les retrouver rapidement ici.**

CTA :

**Explorer les lois**

---

# 36. Error States

Les erreurs doivent expliquer :

**ce qui s’est passé**

**ce que l’utilisateur peut faire**

Exemple :

### Cette source n’est momentanément pas disponible

Le contenu déjà vérifié reste accessible.

**Réessayer**

---

# 37. Motion & Interaction

CODO utilise une animation très contenue.

Spring par défaut :

`stiffness: 100`

`damping: 20`

Durées courtes :

150–350 ms.

Animations uniquement via :

- transform ;
- opacity.

---

# 38. Micro-interactions

Les états actifs peuvent utiliser de légers mouvements perpétuels uniquement lorsqu’ils apportent de l’information.

Exemple :

CODO IA en cours d’analyse :

petite ligne documentaire animée.

Veille active :

pulse très discret.

Ne jamais faire flotter tous les éléments.

---

# 39. Accessibility

WCAG AA minimum.

Contraste élevé.

Navigation clavier complète.

Focus toujours visible.

Lecteurs d’écran.

Libellés sémantiques.

Possibilité d’augmenter la taille du texte.

Mode lecture optimisé.

Lecture audio des explications à terme.

---

# 40. Iconography

Icônes simples en outline.

Épaisseur uniforme.

Style géométrique contemporain.

Ne jamais utiliser d’emoji.

Éviter les symboles juridiques clichés à répétition.

---

# 41. Imagery

CODO utilise très peu de photographie.

Lorsqu’elle est utilisée :

- scènes ivoiriennes contemporaines ;
- personnes réelles ;
- administrations ;
- villes ;
- travail ;
- vie quotidienne ;
- aucun folklore artificiel.

L’imagerie ne doit jamais prendre le dessus sur le contenu juridique.

---

# 42. Source-First Principle

Sur toute réponse susceptible d’entraîner une décision importante, CODO doit rendre accessibles en un geste :

**source**

**article**

**version**

**statut**

**date**

**institution**

---

# 43. AI Disclosure

Les explications produites par l’IA sont identifiées clairement :

**Explication CODO**

et jamais :

**Texte officiel**

Une séparation graphique permanente doit empêcher toute confusion.

---

# 44. Design of Trust

La confiance doit être créée par :

- provenance ;
- dates ;
- références ;
- versionnement ;
- structure ;
- lisibilité ;
- cohérence.

Pas par des slogans comme :

« IA révolutionnaire »

« 100 % fiable »

« expertise absolue ».

---

# 45. Premium Details

Les détails premium de CODO reposent sur :

- alignements précis ;
- typography ;
- espaces ;
- transitions ;
- lecture ;
- cohérence des sources ;
- micro-interactions ;
- hiérarchie documentaire.

Pas sur :

- gradients spectaculaires ;
- glassmorphism ;
- effets 3D ;
- néons ;
- ombres lourdes.

---

# 46. Anti-Patterns — NEVER DO

Ne jamais utiliser :

- Inter ;
- Times New Roman ;
- Georgia ;
- Garamond ;
- noir pur #000000 ;
- néons ;
- glow ;
- boutons violets ou bleus « IA » ;
- gradients multicolores ;
- glassmorphism généralisé ;
- trois cartes identiques côte à côte ;
- Hero centré générique ;
- faux chiffres de confiance ;
- textes génériques type « Next Generation » ;
- « Elevate your experience » ;
- « Seamless » ;
- « Unleash » ;
- flèches « Scroll down » ;
- emojis ;
- curseur personnalisé ;
- animations décoratives excessives ;
- gigantesques H1 occupant tout l’écran ;
- dashboard rempli de KPI sans valeur ;
- illustrations juridiques clichés ;
- marteau de juge omniprésent ;
- balance de justice partout ;
- colonnes gréco-romaines ;
- texte sur images ;
- chevauchements ;
- défilement horizontal mobile ;
- contenu légal sans provenance ;
- article sans statut ;
- réponse IA sans distinction du texte officiel.

---

# 47. Core Screens To Generate in Stitch

Stitch doit produire la famille d’écrans suivante en conservant strictement ce DESIGN.md :

1. **Accueil public CODO**
2. **Recherche universelle**
3. **Résultats de recherche**
4. **CODO IA — conversation**
5. **CODO IA — réponse juridique sourcée**
6. **Lois & Codes**
7. **Explorateur d’un code**
8. **Page article de loi**
9. **Historique d’un article**
10. **Comparaison de versions**
11. **Procédures**
12. **Détail d’une procédure**
13. **Situations de vie**
14. **Résultat d’une situation de vie**
15. **Jurisprudence**
16. **Détail d’une décision**
17. **Institutions**
18. **Détail institution/juridiction**
19. **Actualité et veille juridique**
20. **Mon espace**
21. **Mes favoris**
22. **Mes alertes**
23. **Mes dossiers**
24. **CODO Pro**
25. **Recherche avancée CODO Pro**
26. **Connexion / création de compte**
27. **Onboarding**
28. **Paramètres et accessibilité**
29. **Back-office juridique**
30. **Import d’un nouveau texte**
31. **Validation juridique**
32. **Éditeur de texte**
33. **Gestion des versions**
34. **Gestion des sources**
35. **Audit et traçabilité**

---

# 48. Master UX Principle

Chaque écran doit répondre immédiatement à trois questions :

**Où suis-je ?**

**Quelle information juridique suis-je en train de consulter ?**

**Comment puis-je vérifier sa source ?**

---

# 49. Final Design Statement

CODO doit ressembler à une infrastructure publique numérique de nouvelle génération, et non à un site institutionnel ancien ou à un chatbot IA générique.

L’interface doit faire comprendre :

> **Le droit est complexe derrière la plateforme, mais simple à utiliser devant l’utilisateur.**

Le produit doit combiner :

**la rigueur d’une bibliothèque juridique,  
la simplicité d’un moteur de recherche,  
la pédagogie d’un assistant,  
et la traçabilité d’un système documentaire professionnel.**

---

# CODO

**Centre d’Orientation du Droit et des Obligations**

### Le droit ivoirien, accessible à tous.

**Design principle:**  
**Une question. Une règle. Une source. Une orientation.**