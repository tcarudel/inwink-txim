# txim : effets pour blocs texte + image inwink

Animations d'apparition et effets de survol pour le gabarit « Contenu libre » texte + image d'inwink.
Un effet s'active en ajoutant une classe au bloc ; la plupart fonctionnent **sans aucun JavaScript**.

- 16 animations d'image, 9 animations de texte, 6 effets de survol, combinables entre eux.
- Deux modes : **lié au défilement** (CSS pur, par défaut) ou **joué à l'apparition** (JS léger).
- Réglages par bloc : hauteur de déclenchement, intensité, vitesse.
- Liste complète des classes : [CATALOGUE.md](CATALOGUE.md).

## Installation

CSS, à charger sur tout le site :

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/tcarudel/inwink-txim@0.1.0/dist/txim.css">
```

JS, **uniquement** si un bloc utilise le mode « joué à l'apparition » ou les survols Inclinaison / Projecteur :

```html
<script src="https://cdn.jsdelivr.net/gh/tcarudel/inwink-txim@0.1.0/dist/txim.js" defer></script>
```

Version autonome d'un seul effet (noyau inclus) : `dist/standalone/<famille>-<effet>/`.

## Utilisation

Deux façons de poser les classes, cumulables :

1. **Bloc prêt à l'emploi (recommandé).** `dist/gabarit/bloc-texte-image-txim.json` est un bloc « Contenu libre »
   texte + image complet : gabarit de référence (positions, proportion, carte, opacité), options txim sous forme
   de listes déroulantes, contenu et bouton d'exemple, identifiants aléatoires régénérés à chaque build.
   Dans inwink : créer un nouveau bloc, « Éditer le JSON », tout remplacer par ce fichier, « Valider ».
   Les listes « Animation de l'image », « Animation du texte », « Effet au survol », « Déclenchement »,
   « Hauteur de déclenchement », « Intensité » et « Vitesse » apparaissent alors dans le panneau du bloc ;
   chaque choix devient une classe sur `.content-wrapper` via `conditionalClasses`.
   Ce JSON remplace **tout** le bloc (contenu et boutons compris) : il sert à créer de nouveaux blocs.
   Ensuite, « Modifier les champs » et « Modifier le gabarit » restent utilisables normalement dans inwink.

2. **Classe du bloc.** Ajouter directement les classes au conteneur `#ct-…` :

   ```
   txim-i-rideau txim-t-monte txim-h-zoom txim-seuil-40 txim-force-15
   ```

### Options

| Classe | Effet | Défaut |
|---|---|---|
| `txim-apparition` | joue l'animation une fois quand le bloc franchit la ligne (JS requis) | lié au défilement |
| `txim-seuil-10` … `txim-seuil-50` | hauteur de déclenchement, en % depuis le bas de l'écran | 25 % |
| `txim-force-05`, `-075`, `-15`, `-2` | intensité (amplitude des mouvements) | ×1 |
| `txim-vif`, `txim-pose` | vitesse (course en mode défilement, durée en mode apparition) | normale |

### Variables CSS (réglage fin, par bloc)

```css
#ct-xxxx {
  --txim-seuil: 37%;     /* hauteur de déclenchement */
  --txim-force: 1.3;     /* intensité */
  --txim-course: .8;     /* mode défilement : distance de scroll */
  --txim-duree: 1.2;     /* mode apparition : durées et décalages */
  --txim-accent: #e63;   /* couleur des aplats (défaut : --inwinkaccentcolor) */
  --txim-fond: #fff;     /* fond du texte pour le survol Superposition */
}
```

## Quand le JS est-il nécessaire ?

| Situation | JS |
|---|---|
| Mode lié au défilement (défaut) | non |
| Mode joué à l'apparition (`txim-apparition`) | oui ; sans JS, le bloc s'affiche normalement, sans animation |
| Survols Inclinaison et Projecteur | oui ; sans JS, ils sont inactifs |
| Firefox (pas encore d'`animation-timeline`) | sans JS : blocs affichés sans animation ; avec JS : repli automatique en mode apparition |

Le JS ne modifie jamais `className` ni la structure : il pose des attributs `data-txim-*` et des variables CSS,
et surveille le DOM (les pages inwink changent sans rechargement).

## Points d'attention

- `.picture-wrapper::before` appartient au gabarit (voile clair / sombre) : txim n'utilise que `::after`.
- Sous un effet de texte, `.pretitle` et `.bloctitle` passent en `display: block` (nécessaire aux transformations).
- `.picture-wrapper` passe en `overflow: hidden` dès qu'un effet txim est présent.
- Sur mobile (< 768 px), `.content-wrapper` coupe les débordements horizontaux (`overflow-x: clip`).
- Les parallaxes restent liées au défilement quel que soit le mode.
- `prefers-reduced-motion` : toutes les animations sont désactivées.
- Combinaisons déconseillées : voir [CATALOGUE.md](CATALOGUE.md).

## Développement

```
src/core.css            noyau : options, moteur (défilement / apparition), accessibilité
src/core.js             JS optionnel
src/effets/<famille>/   un fichier CSS par effet (image, texte, survol)
gabarit/base.json       gabarit de référence (source du bloc complet et de la démo)
demo/template.html      démo reproduisant le DOM inwink
build.py                catalogue, macros CSS, génération de dist/ et de CATALOGUE.md
```

`python3 build.py` puis ouvrir `dist/demo/index.html`.
Ajouter un effet : créer `src/effets/<famille>/<cle>.css`, l'ajouter au catalogue dans `build.py`, relancer le build.
Macros disponibles dans les sources : `§F` (force), `§D` (direction), `§A` (accent), `§SELF(classe)`,
`§HV(classe)`, `§PTR(classe)` ; voir `build.py`.
