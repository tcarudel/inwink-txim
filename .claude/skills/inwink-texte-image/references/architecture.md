# Architecture TXIM

## Sommaire
1. DOM du bloc texte + image
2. Où se posent les classes
3. Le moteur : deux modes
4. Variables, ordre d'apparition, cibles
5. Macros des sources CSS
6. Le JS
7. Bloc JSON et gabarit de référence
8. Pièges connus

## 1. DOM du bloc texte + image

```
#ct-<uuid>.dynamicbloc-contentwrapper.bloc-teaser
  └ .dynamiccontentbloc > .bloc-content
      └ .content-wrapper  + image-left|image-right, text-left|text-center|text-right,
                            half|large|small, is-card, image-dark|image-light
          ├ .picture-wrapper > img.picture            (img absente si pas d'image)
          └ .text-wrapper[.card]
              ├ h2.bloc-title > span.pretitle.bloc-accent > span.fieldval > span.fieldtext
              │               > span.bloctitle         > span.fieldval > span.fieldtext
              ├ div.description > span.fieldval > span.fieldtext
              └ .itembloccontentactions > a[role=button]   (0, 1 ou plusieurs)
```

CSS du gabarit (voir `gabarit/base.json`, clé `customCSS`, `##contentid` = `#ct-<uuid>`) :
- `.content-wrapper` en flex ; `image-right` = `row-reverse`.
- `.picture-wrapper` : flex, `position: relative`, `container-type: inline-size` ; sa hauteur vient de l'image
  (`object-fit: contain`, `cover` en mode carte). Aucune marge à faire défiler : une parallaxe passe par
  agrandissement + translation.
- `.picture-wrapper::before` : voile clair ou sombre (`image-light`, `image-dark`), `z-index: 1`.
- Mobile (< 768 px) : `.text-wrapper` passe en `display: contents` (hors carte) et `.bloc-title` remonte
  au-dessus de l'image (`order: -1`).

## 2. Où se posent les classes

Sur `.content-wrapper` (listes déroulantes du bloc JSON, via `conditionalClasses`) **ou** sur `#ct-…` (classe du
bloc). Tout le CSS fonctionne dans les deux cas : sélecteurs descendants (`.txim-i-x .picture-wrapper`) ou `§SELF`,
et les variables CSS héritent. La timeline de défilement est toujours posée sur `.content-wrapper`.

## 3. Le moteur : deux modes

Les effets ne déclarent que `animation-name`. Le noyau (`src/core.css`) applique le reste à toutes les `CIBLES` :

- **Lié au défilement** (défaut, CSS pur, dans `@supports (animation-timeline: view())`) :
  `view-timeline: --txim` sur `.content-wrapper`, `view-timeline-inset: 0% var(--txim-seuil)` (la ligne de
  déclenchement remonte de `--txim-seuil` depuis le bas de l'écran), `animation-range` de
  `entry i*9%*course` à `entry (45% + i*11%)*course`.
- **Joué à l'apparition** (`txim-apparition` + JS) : le JS pose `data-txim-arme` (animations en pause à l'état de
  départ), puis `data-txim-vu` quand le bloc franchit la ligne (lecture), `data-txim-reset` pour rejouer quand le
  bloc ressort par le bas. Durée `--dur` (1 s) × `--txim-duree`, délai `i × 130 ms`.
- **Sécurités** : mode apparition sans JS → `animation-name: none` (contenu affiché) ; navigateur sans
  `animation-timeline` → durée nulle, état final immédiat ; avec le JS, repli automatique en mode apparition ;
  `prefers-reduced-motion` → aucune animation.
- Les parallaxes restent liées au défilement quel que soit le mode (déclarations `!important`).

## 4. Variables, ordre d'apparition, cibles

| Variable | Rôle | Défaut |
|---|---|---|
| `--txim-seuil` | hauteur de la ligne de déclenchement | 25% |
| `--txim-force` | amplitude (macro `§F`) | 1 |
| `--txim-course` | distance de défilement (mode défilement) | 1 |
| `--txim-duree` | multiplicateur de durée et de délai (mode apparition) | 1 |
| `--txim-dir` | 1 image à gauche, -1 image à droite (macro `§D`) | 1 |
| `--txim-origine` | origine horizontale selon l'alignement du texte (0%, 50%, 100%) | 0% |
| `--txim-accent` | couleur des aplats (macro `§A`, repli `--inwinkaccentcolor`) | |
| `--txim-fond` | fond du texte pour le survol Superposition | #fff |
| `--txim-dt` | décalage de l'ordre du texte, posé par un effet d'image (Balayage : 4) | 0 |
| `--txim-sens` | sens d'un glissement latéral (keyframe `txim-lateral`) | 1 |
| `--i` | rang d'apparition : image 0, pré-titre 1, titre 2, description 3, boutons 4, 4.5, 5 | |
| `--dur` | durée propre d'un effet en mode apparition | 1s |

Keyframes communes du noyau : `txim-monte`, `txim-lateral`, `txim-apparait`, `txim-dezoom`.

`CIBLES` (build.py) : `.content-wrapper` et ses `.picture-wrapper`, `.picture-wrapper::after`, `.picture`,
`.pretitle`, `.bloctitle`, `.fieldtext`, `.description`, `.itembloccontentactions>*`. Un élément animé hors de
cette liste n'est pas piloté par le moteur.

## 5. Macros des sources CSS

Développées par `build.py` (fonction `developper`) :

| Macro | Devient |
|---|---|
| `§F`, `§D`, `§A` | `var(--txim-force,1)`, `var(--txim-dir,1)`, couleur d'accent |
| `§CW` | tout `.content-wrapper` concerné par une classe txim (sur lui ou sur `#ct`) |
| `§CWT` | idem, avec un effet de texte |
| `§APP` | `.content-wrapper` en mode apparition |
| `§SELF(c)`, `§HV(c)` | `:is(.c .content-wrapper, .content-wrapper.c)` |
| `§PTR(c)` | idem + `[data-txim-pointeur]` (le JS suit le pointeur) |
| `§T<<base>>` | la liste des `CIBLES` sous `base` (réservé au noyau) |

## 6. Le JS (`src/core.js`)

Optionnel. Ne modifie jamais `className` ni la structure : attributs `data-txim-*` et variables CSS uniquement.
- `scan()` au chargement puis à chaque mutation du DOM ou de classe (MutationObserver, regroupé par frame) :
  arme/désarme les blocs en mode apparition, suit le pointeur pour `POINTEUR` (`--txim-px`, `--txim-py`, `--txim-src`).
- Un IntersectionObserver par hauteur (`--txim-seuil` lu avec `getComputedStyle`), un autre pour rejouer.
- API : `TXIM.scan()`, `TXIM.rejouer()`, `TXIM.version`.

## 7. Bloc JSON et gabarit de référence

`gabarit/base.json` est le bloc « Contenu libre » de référence (identifiants `__ID__`, `__ID_ACTION__`).
`build.py` (fonction `bloc_complet`) ajoute les champs `txim-image`, `txim-texte`, `txim-survol`, `txim-mode`,
`txim-hauteur`, `txim-intensite`, `txim-vitesse`, leurs règles `conditionalClasses`, les valeurs par défaut
(`DONNEES_TXIM`) et des UUID neufs → `dist/gabarit/bloc-texte-image-txim.json`. Les valeurs de chaque liste sont
les clés d'effet ; la règle `txim-i-<cle>` teste `txim-image == <cle>`.

## 8. Pièges connus

- `.pretitle` et `.bloctitle` sont des `span` en ligne : le noyau les passe en `display: block` sous un effet de
  texte (les transformations ne s'appliquent pas aux éléments en ligne). `.fieldtext` reste en ligne : c'est lui
  qu'il faut viser pour un effet ligne par ligne (dégradé + `box-decoration-break: clone`).
- `-webkit-text-fill-color: transparent` plutôt que `color: transparent` quand on a besoin de `currentColor`.
- `.picture-wrapper` passe en `overflow: hidden` dès qu'une classe txim est présente ; son `box-shadow` reste visible.
- Mobile : `.content-wrapper` en `overflow-x: clip` (pas de barre horizontale pendant les glissements).
- Une animation en `fill-mode: both` écrase les transitions de la même propriété : d'où `transform` à l'apparition
  et `scale`/`translate`/`rotate` au survol.
- `::after` et `filter` sur `.picture` sont partagés entre familles → `CONFLITS`.
- Propriété personnalisée animée : la déclarer avec `@property`, poser la propriété qui l'utilise (mask-image,
  background…) sur l'élément et n'animer **que la variable**. Si la propriété dépendante figure dans les
  keyframes, Chrome la fige à sa première valeur (bug réel de Volets en 0.1.0, détecté par le test de
  progression). Au repos, la variable vaut sa valeur finale (`initial-value`) : le contenu reste affiché.
- Masques en bandes : une couche de dégradé par bande, légèrement chevauchantes au repos (12,6 % pour des pas de
  12,5 %), plutôt qu'un `repeating-linear-gradient` qui laisse des filets à la fin.
- Images en `loading="lazy"` : ne pas les masquer avec `display: none` ; l'opacité et le clip-path conviennent.
