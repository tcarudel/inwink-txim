# Catalogue txim v0.1.0

Fichier généré par `build.py` : ne pas modifier à la main.

## Animation de l'image

| Classe | Effet | Description | JS |
|---|---|---|---|
| `txim-i-fondu` | Fondu montant | L'image monte en apparaissant. | non |
| `txim-i-rideau` | Rideau | L'image se dévoile depuis son bord extérieur en se dézoomant. | non |
| `txim-i-parallaxe` | Parallaxe | L'image défile dans son cadre (toujours liée au défilement). | non |
| `txim-i-convergence` | Convergence | L'image arrive de son bord extérieur en se redressant. | non |
| `txim-i-cercle` | Ouverture circulaire | L'image s'ouvre en cercle depuis son centre. | non |
| `txim-i-volets` | Volets | L'image se dévoile par bandes horizontales. | non |
| `txim-i-eclosion` | Éclosion | L'image part d'une pastille ronde et s'agrandit. | non |
| `txim-i-portes` | Portes | Deux panneaux de couleur d'accent s'écartent. | non |
| `txim-i-balayage` | Balayage | Un aplat couvre le cadre puis se retire ; le texte attend. | non |
| `txim-i-diagonale` | Diagonale | L'image se dévoile en diagonale depuis le coin extérieur. | non |
| `txim-i-pivot` | Pivot | L'image arrive en tournant et en grossissant. | non |
| `txim-i-depliage` | Dépliage | L'image se déplie en 3D depuis son bord. | non |
| `txim-i-atterrissage` | Atterrissage | L'image arrive en grand par-dessus le texte puis se pose. | non |
| `txim-i-couleur` | Noir et blanc vers couleur | L'image passe du noir et blanc à la couleur. | non |
| `txim-i-flou` | Mise au point (bloc entier) | Le bloc passe du flou au net. | non |
| `txim-i-bascule` | Bascule 3D (bloc entier) | Le bloc arrive incliné et se redresse. | non |

## Animation du texte

| Classe | Effet | Description | JS |
|---|---|---|---|
| `txim-t-monte` | Montée | Les éléments montent l'un après l'autre. | non |
| `txim-t-glisse` | Glissement latéral | Les éléments glissent depuis le bord opposé à l'image. | non |
| `txim-t-fondu` | Fondu | Fondu simple, élément par élément. | non |
| `txim-t-emergence` | Émergence | Chaque élément sort d'une fente invisible. | non |
| `txim-t-focale` | Focale | Le titre arrive agrandi et flou puis se pose net. | non |
| `txim-t-surligneur` | Surligneur | Un trait de surligneur passe sous le titre. | non |
| `txim-t-encre` | Encre | Titre et description se remplissent ligne par ligne. | non |
| `txim-t-zigzag` | Zigzag | Les éléments arrivent alternativement de gauche et de droite. | non |
| `txim-t-parallaxe` | Parallaxe | Le texte se décale pendant la traversée de l'écran. | non |

## Effet au survol

| Classe | Effet | Description | JS |
|---|---|---|---|
| `txim-h-zoom` | Zoom et soulignement | L'image se rapproche, le titre se souligne. | non |
| `txim-h-duotone` | Duotone | La teinte d'accent glisse et révèle la couleur. | non |
| `txim-h-aplat` | Aplat décalé | L'image vient se poser sur un aplat décalé. | non |
| `txim-h-inclinaison` | Inclinaison (JS) | L'image s'incline vers le pointeur. | requis |
| `txim-h-projecteur` | Projecteur (JS) | Un halo suit le pointeur et révèle la couleur. | requis |
| `txim-h-superposition` | Superposition | Le texte glisse par-dessus l'image. | non |

## Options

| Champ du gabarit | Valeur | Classe |
|---|---|---|
| Déclenchement de l'animation | Lié au défilement (défaut, sans JS) | (aucune) |
| Déclenchement de l'animation | Joué à l'apparition (JS) | `txim-apparition` |
| Hauteur de déclenchement | 10 % du bas de l'écran | `txim-seuil-10` |
| Hauteur de déclenchement | 20 % | `txim-seuil-20` |
| Hauteur de déclenchement | 25 % (défaut) | (aucune) |
| Hauteur de déclenchement | 30 % | `txim-seuil-30` |
| Hauteur de déclenchement | 40 % | `txim-seuil-40` |
| Hauteur de déclenchement | 50 % (milieu) | `txim-seuil-50` |
| Intensité | Très légère | `txim-force-05` |
| Intensité | Légère | `txim-force-075` |
| Intensité | Normale (défaut) | (aucune) |
| Intensité | Forte | `txim-force-15` |
| Intensité | Très forte | `txim-force-2` |
| Vitesse | Vive | `txim-vif` |
| Vitesse | Normale (défaut) | (aucune) |
| Vitesse | Posée | `txim-pose` |

## Combinaisons déconseillées

- `txim-i-balayage`, `txim-i-portes` avec `txim-h-duotone`, `txim-h-inclinaison`, `txim-h-projecteur` : même pseudo-élément ::after.
- `txim-i-couleur` avec `txim-h-duotone`, `txim-h-projecteur` : même propriété filter sur l'image.
