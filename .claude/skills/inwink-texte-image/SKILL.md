---
name: inwink-texte-image
description: Crée, adapte ou corrige des effets d'animation pour les blocs texte + image inwink (gabarit « Contenu libre », bloc teaser) dans la bibliothèque TXIM (classes txim-*) — apparition liée au défilement, animation jouée à l'apparition, effets au survol — et génère le bloc inwink complet (JSON) avec toutes les options. Utiliser cette skill dès que l'utilisateur partage une inspiration (vidéo, CodePen, site en production, capture) d'animation d'image ou de texte au scroll, à l'apparition ou au survol, demande d'ajouter ou modifier un effet txim, de régénérer la bibliothèque, un standalone ou un bloc JSON texte + image, ou parle d'animer un bloc texte + image inwink, même sans prononcer « txim ». Pour les carrousels de listes d'items, utiliser inwink-carousel ; pour l'apparence d'une carte de liste, inwink-item-style.
---

# Effets pour blocs texte + image inwink (bibliothèque TXIM)

TXIM anime le bloc « Contenu libre » texte + image d'inwink quand on lui ajoute des classes : `txim-i-<cle>`
(image), `txim-t-<cle>` (texte), `txim-h-<cle>` (survol), plus des options (mode, hauteur, intensité, vitesse).
Livrables : `txim.css` (tout, chargé globalement), `txim.js` (optionnel), un dossier autonome par effet, et un
**bloc inwink complet** (`bloc-texte-image-txim.json`) dont les listes déroulantes posent les classes.

Trois missions types :

- **A. Nouvel effet à partir d'une inspiration** : étapes 0 à 7.
- **B. Modifier ou corriger un effet** : étapes 0, 4, 6, 7 (la démo légère de l'étape 2 si le rendu change).
- **C. Générer un ou plusieurs blocs JSON** : étape 0 puis section « Mission C ».

## 0. Trouver le dépôt TXIM (étape bloquante)

- **Claude Code** : le dépôt est normalement le projet courant. Repères : `src/core.css`, `src/effets/`,
  `build.py`, `gabarit/base.json`.
- **Chat (claude.ai)**, reconnaissable à l'absence de ces fichiers : **avant toute autre action** (y compris ouvrir
  l'inspiration ou proposer un effet), vérifie qu'un zip du dépôt a été joint. S'il n'y en a pas, **arrête-toi et
  demande-le** en une phrase : « Pour partir de la dernière version de ta bibliothèque, peux-tu m'envoyer le zip de
  ton dépôt inwink-txim (celui qui contient `src/` et `build.py`) ? ». Pourquoi : le chat repart de zéro à chaque
  conversation ; sans le dépôt à jour, l'effet serait écrit sur un noyau obsolète et écraserait des modifications.
- Refuse un zip sans `src/core.css` ni `build.py` (par exemple le zip `dist`) : explique la différence et redemande.
  Décompresse le bon zip dans le répertoire de travail avant toute modification.

Ne réécris jamais le noyau de mémoire : lis `src/core.css`, `src/core.js` et `build.py` de la version en cours.

## 1. Comprendre l'inspiration

1. **Vidéo ou site en production** : `web_fetch` ne rend pas le mouvement. Si Claude in Chrome est disponible,
   ouvre la page, fais défiler par petits pas et prends plusieurs captures pour comprendre le **mouvement** ;
   survole les éléments si l'effet est au survol. Si une vidéo reste figée, demande de mettre la fenêtre Chrome au
   premier plan. Sans accès, demande 2 ou 3 captures (début, milieu, fin) ou une description.
2. **CodePen** : la page est souvent illisible via `web_fetch`. Demande à l'utilisateur de coller le CSS/JS du pen
   (ou tente l'extension Chrome). Le code d'un pen est une inspiration, pas du code à copier : il cible un DOM qui
   n'est pas celui d'inwink.
3. **Reformule l'effet** en 2 ou 3 phrases et fais-le valider avant de coder : déclencheur (lié au défilement,
   joué à l'apparition, survol), éléments animés (image, pré-titre, titre, description, boutons, bloc entier),
   mouvement. Signale tout de suite ce qui exige de **modifier le DOM** (découper un titre en lettres ou en mots,
   ajouter des éléments, dupliquer l'image) : c'est interdit dans inwink (React). Propose une alternative CSS
   (ligne par ligne via `.fieldtext` en ligne, masques, dégradés, `::after`), ou le JS minimal qui ne pose que des
   variables CSS et des attributs `data-txim-*`.

## 2. Démo légère de validation

Avant d'adapter quoi que ce soit à inwink, montre l'effet dans une page HTML autonome et légère, construite à partir
de `assets/demo-legere.html` (bloc générique, pas le DOM inwink). Propose 1 à 3 variantes si l'inspiration laisse
une marge d'interprétation, avec un curseur d'intensité si utile. Livre le fichier et **attends la validation**.

Pourquoi : on sépare « l'effet est-il réussi ? » de « tient-il dans le gabarit inwink ? ». Retoucher une démo de
50 lignes est bien plus rapide que retoucher un effet déjà branché dans la bibliothèque.

Passe cette étape seulement si l'utilisateur dit que l'effet est déjà validé, ou pour une correction mineure.

## 3. Choisir la famille et nommer

- **image** (`txim-i-`) : anime `.picture-wrapper`, `.picture`, `.picture-wrapper::after`, ou le bloc entier
  (`.content-wrapper`, via `§SELF`).
- **texte** (`txim-t-`) : anime `.pretitle`, `.bloctitle`, `.description`, `.itembloccontentactions>*`, `.fieldtext`.
- **survol** (`txim-h-`) : transitions déclenchées au survol et au focus clavier.

Une inspiration qui anime image **et** texte se découpe en deux effets (un image, un texte) : c'est ce qui permet à
l'utilisateur de les combiner librement dans le panneau du bloc. Crée un seul effet « bloc entier » seulement si le
mouvement est indissociable (le bloc bascule d'un seul tenant).

Clé : courte, en français, sans accent ni espace (`volets`, `emergence`). Vérifie qu'elle n'existe pas déjà dans la
famille (`IMAGES`, `TEXTES`, `SURVOLS` dans `build.py`).

## 4. Écrire l'effet

Crée `src/effets/<famille>/<cle>.css` à partir de `assets/template-<famille>.css` et inspire-toi de l'effet
existant le plus proche. Lis `references/architecture.md` (DOM, moteur, macros, pièges) avant d'écrire.

Règles, et pourquoi :

- **L'effet ne déclare que `animation-name`** (plus au besoin `--dur`, `--i`, `--txim-dt`, `--txim-sens`). Le noyau
  fournit timeline, durée, délai, courbe et mode. N'utilise jamais le raccourci `animation:` : il effacerait les
  réglages du moteur.
- **Keyframes : n'écrire que l'état de départ (`from`).** L'état naturel est l'état final ; ainsi, sans JS, sans
  support navigateur ou avec « réduire les animations », le contenu reste affiché. Si un `to` est nécessaire
  (clip-path, propriété personnalisée), il doit être identique au rendu naturel.
- **Variable animée** (masque en bandes, dégradé qui progresse…) : déclare-la avec `@property`, pose la propriété
  qui l'utilise **sur l'élément** et n'anime **que la variable** dans les keyframes. Une propriété qui dépend d'une
  variable animée par les mêmes keyframes est figée par Chrome à sa première valeur (voir `image/volets.css`).
- **Macros** : `§F` pour toute amplitude (distance, angle, flou, zoom), `§D` pour tout sens gauche/droite (l'effet
  doit se retourner quand l'image est à droite), `§A` pour la couleur d'accent. Jamais de couleur figée : utilise
  `§A` ou `currentColor`.
- **Apparition = `transform` ; survol = propriétés séparées `scale`, `translate`, `rotate`.** Elles se composent,
  donc un effet d'apparition et un effet de survol restent combinables.
- **Pseudo-élément : uniquement `.picture-wrapper::after`.** `::before` appartient au gabarit (voile clair/sombre).
  Un effet qui utilise `::after` ou `filter` sur `.picture` entre en conflit avec d'autres : déclare-le dans
  `CONFLITS` (`build.py`).
- **Ne jamais animer `.text-wrapper` à l'apparition** : il passe en `display: contents` sur mobile (aucune boîte).
- **Nouvel élément animé** hors de la liste `CIBLES` (`build.py`) : ajoute-le à `CIBLES`, sinon le moteur ne le
  pilote pas.
- **Effet toujours lié au défilement** (type parallaxe) : recopie le bloc `!important` de `image/parallaxe.css`.
- **Survol** : dans `@media (hover:hover) and (prefers-reduced-motion:no-preference)`, déclenché par
  `§HV(txim-h-<cle>):is(:hover,:focus-within)`. S'il a besoin de la position du pointeur, utilise
  `§PTR(txim-h-<cle>)` et ajoute la classe à `POINTEUR` dans `src/core.js`.
- **Préfixe `txim-`** pour les keyframes et les propriétés personnalisées ; jamais de modification de `className`
  ni de structure (React).
- **JS** : uniquement si le CSS ne suffit pas, dans `src/core.js`, en posant des variables CSS ou des attributs
  `data-txim-*`, avec nettoyage quand la classe disparaît (voir `suivre()`), et en marquant l'effet « JS requis ».

## 5. Brancher dans le build

Dans `build.py`, ajoute une ligne à `IMAGES`, `TEXTES` ou `SURVOLS` :
`("<cle>", "<Nom fr>", "<Name en>", "<Nombre es>", "<Description courte>", <JS requis>)`, et une entrée à
`CONFLITS` si besoin. Tout le reste est généré : bibliothèque, autonomes, listes et règles du bloc JSON,
`CATALOGUE.md`, démo. Une nouvelle **option** (autre que les effets) s'ajoute à `OPTIONS` et à `src/core.css`.

## 6. Construire et tester

```bash
python3 build.py
python3 <chemin-de-la-skill>/scripts/smoke_test.py . --only i-<cle>      # ou t-<cle>, h-<cle>
```

Le test vérifie la cohérence du catalogue et du bloc JSON, l'absence de macro non développée, que **chaque** effet
anime bien quelque chose (défilement, mode apparition, survol), l'absence d'erreur JS et de débordement horizontal
sur mobile, et enregistre des captures à mi-animation dans `dist/screens/` pour les effets passés à `--only`.
**Regarde les captures** (image à gauche, image à droite, carte), et au moins un effet voisin pour détecter une
régression du noyau. Si Playwright manque : `pip install playwright && playwright install chromium`.

## 7. Livrer

La publication est automatisée : `VERSION` (dans `build.py`) est la seule source du numéro, et la GitHub Action
`.github/workflows/release.yml` crée le tag `vX.Y.Z` et la release (notes tirées de `CHANGELOG.md`) dès qu'un push
sur `main` contient une nouvelle `VERSION`. Ton rôle s'arrête au commit local.

```bash
python3 <chemin-de-la-skill>/scripts/livrer.py . <mineure|patch|majeure> "Entrée de changelog" ["Autre entrée"] [--commit]
```

Le script incrémente `VERSION` (**mineure** pour un nouvel effet ou une nouvelle option, **patch** pour une
correction, **majeure** seulement si des classes existantes changent de nom ou disparaissent : les blocs en
production cesseraient de fonctionner), ajoute la section du changelog, relance le build et le test. Rédige des
entrées de changelog courtes et orientées utilisateur (« Nouvel effet d'image : Lames (`txim-i-lames`) »).

- **Claude Code** : montre le résumé des modifications (`git status`, diff utile), puis lance le script avec
  `--commit`. **Ne pousse jamais** sans demande explicite (« push ») : c'est le push qui publie, via l'Action.
- **Chat** : lance le script sans `--commit`, puis livre un zip du dépôt mis à jour (sources + `dist/`, sans
  `dist/*.zip` ni `dist/screens/`), `dist/demo/demo-autonome.html` et `dist/gabarit/bloc-texte-image-txim.json`.
  Rappelle la marche à suivre : remplacer le contenu du clone local **sauf `.git`** par celui du zip, puis
  commit et « Push origin » dans GitHub Desktop ; l'Action fait le reste.

Termine par un résumé court : classe(s) à utiliser et nom dans le panneau, famille, JS requis ou non, conflits,
points d'attention, nouvelle version et URL jsDelivr
(`https://cdn.jsdelivr.net/gh/tcarudel/inwink-txim@vX.Y.Z/dist/txim.css`, idem `txim.js`).

## Mission C : générer des blocs JSON

Le bloc complet est `dist/gabarit/bloc-texte-image-txim.json` : gabarit de référence (`gabarit/base.json`) + listes
txim + règles `conditionalClasses` + contenu et bouton d'exemple. Pour de nouveaux identifiants, sans rebuild :

```bash
python3 <chemin-de-la-skill>/scripts/nouveau_bloc.py . [nombre] [--data txim-image=rideau --data card=true …]
```

Chaque fichier a ses propres UUID (bloc et bouton). Rappelle à l'utilisateur que ce JSON **remplace tout le bloc**
(contenu et boutons compris) : il sert à **créer** un bloc via « Éditer le JSON ». Il faut aussi que `txim.css` soit
chargé sur le site (et `txim.js` pour le mode apparition ou les survols JS). Pour changer le gabarit de référence
(nouvelle option de mise en page, CSS), modifie `gabarit/base.json` puis relance le build.

## Références

- `references/architecture.md` : DOM du bloc, moteur (deux modes), variables, macros, cibles, pièges connus.
- `assets/template-image.css`, `template-texte.css`, `template-survol.css` : modèles d'effet.
- `assets/demo-legere.html` : modèle de démo légère (étape 2).
- `scripts/smoke_test.py` : test automatique ; `scripts/nouveau_bloc.py` : blocs JSON avec identifiants neufs ;
  `scripts/livrer.py` : version, changelog, build, test, commit local.
