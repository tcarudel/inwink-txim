#!/usr/bin/env python3
"""Construit la bibliothèque txim (effets pour blocs texte + image inwink).

    python3 build.py   -> génère dist/ (bibliothèque, autonomes, bloc inwink complet, démo) et CATALOGUE.md
"""
import json, re, shutil, uuid, zipfile
from pathlib import Path

VERSION = "0.1.0"
RACINE = Path(__file__).parent
SRC, DIST = RACINE / "src", RACINE / "dist"
PREFIXE = "txim"

# ---------------------------------------------------------------- catalogue
# (clé, fr, en, es, description, JS requis)
IMAGES = [
    ("fondu", "Fondu montant", "Fade up", "Fundido ascendente", "L'image monte en apparaissant.", False),
    ("rideau", "Rideau", "Curtain", "Cortina", "L'image se dévoile depuis son bord extérieur en se dézoomant.", False),
    ("parallaxe", "Parallaxe", "Parallax", "Paralaje", "L'image défile dans son cadre (toujours liée au défilement).", False),
    ("convergence", "Convergence", "Converge", "Convergencia", "L'image arrive de son bord extérieur en se redressant.", False),
    ("cercle", "Ouverture circulaire", "Circle reveal", "Apertura circular", "L'image s'ouvre en cercle depuis son centre.", False),
    ("volets", "Volets", "Blinds", "Persianas", "L'image se dévoile par bandes horizontales.", False),
    ("eclosion", "Éclosion", "Bloom", "Eclosión", "L'image part d'une pastille ronde et s'agrandit.", False),
    ("portes", "Portes", "Doors", "Puertas", "Deux panneaux de couleur d'accent s'écartent.", False),
    ("balayage", "Balayage", "Wipe", "Barrido", "Un aplat couvre le cadre puis se retire ; le texte attend.", False),
    ("diagonale", "Diagonale", "Diagonal", "Diagonal", "L'image se dévoile en diagonale depuis le coin extérieur.", False),
    ("pivot", "Pivot", "Pivot", "Giro", "L'image arrive en tournant et en grossissant.", False),
    ("depliage", "Dépliage", "Unfold", "Despliegue", "L'image se déplie en 3D depuis son bord.", False),
    ("atterrissage", "Atterrissage", "Landing", "Aterrizaje", "L'image arrive en grand par-dessus le texte puis se pose.", False),
    ("couleur", "Noir et blanc vers couleur", "Black & white to color", "Blanco y negro a color", "L'image passe du noir et blanc à la couleur.", False),
    ("flou", "Mise au point (bloc entier)", "Focus (whole block)", "Enfoque (bloque entero)", "Le bloc passe du flou au net.", False),
    ("bascule", "Bascule 3D (bloc entier)", "3D tilt-up (whole block)", "Basculación 3D (bloque entero)", "Le bloc arrive incliné et se redresse.", False),
]
TEXTES = [
    ("monte", "Montée", "Rise", "Subida", "Les éléments montent l'un après l'autre.", False),
    ("glisse", "Glissement latéral", "Side slide", "Deslizamiento lateral", "Les éléments glissent depuis le bord opposé à l'image.", False),
    ("fondu", "Fondu", "Fade", "Fundido", "Fondu simple, élément par élément.", False),
    ("emergence", "Émergence", "Emerge", "Emergencia", "Chaque élément sort d'une fente invisible.", False),
    ("focale", "Focale", "Focus title", "Focal", "Le titre arrive agrandi et flou puis se pose net.", False),
    ("surligneur", "Surligneur", "Highlighter", "Resaltador", "Un trait de surligneur passe sous le titre.", False),
    ("encre", "Encre", "Ink fill", "Tinta", "Titre et description se remplissent ligne par ligne.", False),
    ("zigzag", "Zigzag", "Zigzag", "Zigzag", "Les éléments arrivent alternativement de gauche et de droite.", False),
    ("parallaxe", "Parallaxe", "Parallax", "Paralaje", "Le texte se décale pendant la traversée de l'écran.", False),
]
SURVOLS = [
    ("zoom", "Zoom et soulignement", "Zoom & underline", "Zoom y subrayado", "L'image se rapproche, le titre se souligne.", False),
    ("duotone", "Duotone", "Duotone", "Duotono", "La teinte d'accent glisse et révèle la couleur.", False),
    ("aplat", "Aplat décalé", "Offset block", "Bloque desplazado", "L'image vient se poser sur un aplat décalé.", False),
    ("inclinaison", "Inclinaison (JS)", "Tilt (JS)", "Inclinación (JS)", "L'image s'incline vers le pointeur.", True),
    ("projecteur", "Projecteur (JS)", "Spotlight (JS)", "Foco (JS)", "Un halo suit le pointeur et révèle la couleur.", True),
    ("superposition", "Superposition", "Overlap", "Superposición", "Le texte glisse par-dessus l'image.", False),
]
FAMILLES = [("image", "i", IMAGES), ("texte", "t", TEXTES), ("survol", "h", SURVOLS)]
# Combinaisons qui se disputent la même propriété (documentées, signalées dans la démo)
CONFLITS = [
    ({"i-portes", "i-balayage"}, {"h-duotone", "h-inclinaison", "h-projecteur"}, "même pseudo-élément ::after"),
    ({"i-couleur"}, {"h-duotone", "h-projecteur"}, "même propriété filter sur l'image"),
]
# Options : (clé du champ, fr, en, es, [(valeur, fr, en, es, classe ou None)])
OPTIONS = [
    ("txim-mode", "Déclenchement de l'animation", "Animation trigger", "Activación de la animación", [
        ("defilement", "Lié au défilement (défaut, sans JS)", "Linked to scroll (default, no JS)", "Vinculada al desplazamiento (sin JS)", None),
        ("apparition", "Joué à l'apparition (JS)", "Played on appearance (JS)", "Reproducida al aparecer (JS)", "txim-apparition")]),
    ("txim-hauteur", "Hauteur de déclenchement", "Trigger height", "Altura de activación", [
        ("10", "10 % du bas de l'écran", "10% from bottom", "10 % desde abajo", "txim-seuil-10"),
        ("20", "20 %", "20%", "20 %", "txim-seuil-20"),
        ("25", "25 % (défaut)", "25% (default)", "25 % (por defecto)", None),
        ("30", "30 %", "30%", "30 %", "txim-seuil-30"),
        ("40", "40 %", "40%", "40 %", "txim-seuil-40"),
        ("50", "50 % (milieu)", "50% (middle)", "50 % (centro)", "txim-seuil-50")]),
    ("txim-intensite", "Intensité", "Intensity", "Intensidad", [
        ("05", "Très légère", "Very light", "Muy ligera", "txim-force-05"),
        ("075", "Légère", "Light", "Ligera", "txim-force-075"),
        ("1", "Normale (défaut)", "Normal (default)", "Normal (por defecto)", None),
        ("15", "Forte", "Strong", "Fuerte", "txim-force-15"),
        ("2", "Très forte", "Very strong", "Muy fuerte", "txim-force-2")]),
    ("txim-vitesse", "Vitesse", "Speed", "Velocidad", [
        ("vif", "Vive", "Brisk", "Viva", "txim-vif"),
        ("normal", "Normale (défaut)", "Normal (default)", "Normal (por defecto)", None),
        ("pose", "Posée", "Calm", "Pausada", "txim-pose")]),
]

# ---------------------------------------------------------------- macros CSS
def _is(a, b): return f":is({a},{b})"
CW = _is('[class*="txim-"] .content-wrapper', '.content-wrapper[class*="txim-"]')
MACROS = {
    "§CWT": _is('[class*="txim-t-"] .content-wrapper', '.content-wrapper[class*="txim-t-"]'),
    "§CW": CW,
    "§APP": _is(".txim-apparition .content-wrapper", ".content-wrapper.txim-apparition"),
    "§F": "var(--txim-force,1)",
    "§D": "var(--txim-dir,1)",
    "§A": "var(--txim-accent,var(--inwinkaccentcolor,#2F4BE0))",
    "§VERSION": VERSION,
}
CIBLES = ["", " .picture-wrapper", " .picture-wrapper::after", " .picture", " .pretitle",
          " .bloctitle", " .fieldtext", " .description", " .itembloccontentactions>*"]

def developper(css):
    css = re.sub(r"§(SELF|HV)\(([\w-]+)\)", lambda m: _is(f".{m[2]} .content-wrapper", f".content-wrapper.{m[2]}"), css)
    css = re.sub(r"§PTR\(([\w-]+)\)", lambda m: _is(f".{m[1]} .content-wrapper", f".content-wrapper.{m[1]}") + "[data-txim-pointeur]", css)
    for k in sorted(MACROS, key=len, reverse=True):
        css = css.replace(k, MACROS[k])
    return re.sub(r"§T<<(.+?)>>", lambda m: ",\n".join(m[1] + c for c in CIBLES), css)

def entete(titre):
    return f"/*! {PREFIXE} v{VERSION} | {titre} | https://github.com/tcarudel/inwink-txim */\n"

# ---------------------------------------------------------------- gabarit
def champ_liste(cle, fr, en, es, valeurs):
    return {
        "key": cle, "isMandatory": False, "isMandatoryFor": None, "applyTo": [], "isLocalizable": False,
        "isStatic": False, "isLocked": False, "type": "selectlist",
        "labels": {"fr": fr, "en": en, "es": es},
        "placeholders": None, "descriptions": None, "remarks": None, "tooltip": None, "values": None,
        "valuesList": [{"isSelectable": True, "key": v[0], "labels": {"fr": v[1], "en": v[2], "es": v[3]},
                        "valuesList": None} for v in valeurs],
        "value": None, "validations": None, "scope": []}

def champs_et_regles():
    """Champs (listes déroulantes) et règles conditionalClasses des options txim."""
    champs, regles = [], {}
    libelles = {"image": ("Animation de l'image", "Image animation", "Animación de la imagen"),
                "texte": ("Animation du texte", "Text animation", "Animación del texto"),
                "survol": ("Effet au survol", "Hover effect", "Efecto al pasar el ratón")}
    for fam, lettre, liste in FAMILLES:
        cle = f"txim-{fam}"
        champs.append(champ_liste(cle, *libelles[fam], [(e[0], e[1], e[2], e[3]) for e in liste]))
        for e in liste:
            regles[f"txim-{lettre}-{e[0]}"] = [{"name": cle, "op": "eq", "val": e[0]}]
    for cle, fr, en, es, valeurs in OPTIONS:
        champs.append(champ_liste(cle, fr, en, es, valeurs))
        for v in valeurs:
            if v[4]:
                regles[v[4]] = [{"name": cle, "op": "eq", "val": v[0]}]
    return champs, regles

# Valeurs par défaut d'un nouveau bloc (effet visible dès la création, modifiable dans le panneau)
DONNEES_TXIM = {"txim-image": "fondu", "txim-texte": "monte", "txim-survol": None, "txim-mode": "defilement",
                "txim-hauteur": "25", "txim-intensite": "1", "txim-vitesse": "normal"}

def bloc_complet():
    """Bloc inwink complet, à coller dans « Éditer le JSON » d'un nouveau bloc.
    Gabarit de référence (gabarit/base.json) + options txim + contenu d'exemple + identifiants aléatoires."""
    g = json.loads((RACINE / "gabarit" / "base.json").read_text(encoding="utf-8"))
    g["id"] = str(uuid.uuid4())
    for a in g["actions"]: a["id"] = str(uuid.uuid4())
    p = g["properties"]
    champs, regles = champs_et_regles()
    p["itemDefinition"]["fields"] += champs
    p["itemDefinition"]["scopes"].update({c["key"]: [] for c in champs})
    p["template"]["conditionalClasses"].update(regles)
    p["data"].update(DONNEES_TXIM)
    return g

# ---------------------------------------------------------------- démo
TEXTES_DEMO = [
    ("Le programme", "Trois jours pour repenser l'événementiel hybride", "Plénières, ateliers pratiques et rendez-vous d'affaires : composez votre parcours à l'avance et recevez vos rappels sur l'application.", ["Voir le programme"]),
    ("Le lieu", "Un ancien entrepôt industriel au bord du canal", "4 000 m² sur deux niveaux, une verrière centrale et trois salles modulables pour les sessions en petit comité.", ["Découvrir le lieu", "Plan d'accès"]),
    ("Networking", "Des rencontres planifiées, pas laissées au hasard", "Indiquez vos centres d'intérêt : l'application vous propose des rendez-vous de vingt minutes avec les participants proches de vos sujets.", ["Préparer mes rendez-vous"]),
    ("Replays", "Toutes les plénières disponibles en replay", "Les vidéos sont en ligne le soir même, avec les supports des intervenants et un résumé de chaque session.", ["Accéder aux replays"]),
]
MISES_EN_PAGE = [  # classes du gabarit, légende
    ("image-left text-left half", "Image à gauche, texte à gauche, moitié"),
    ("image-right text-center large", "Image à droite, texte centré, texte large"),
    ("image-left text-center half is-card", "Carte, image à gauche, texte centré"),
    ("image-right text-right small is-card image-dark", "Carte, image à droite, texte à droite, texte petit, image sombre"),
]
IMAGES_DEMO = ["https://cdn-assets.inwink.com/backoffice-public/assets/pictures/00-inwink/Background_Blue.jpg",
               "https://picsum.photos/seed/txim2/1200/800", "https://picsum.photos/seed/txim3/1200/800",
               "https://picsum.photos/seed/txim4/1200/800"]

def bloc_inwink(n, classes, txt, img, css_gabarit):
    uid = f"00000000-0000-4000-8000-00000000000{n}"
    card = " card" if "is-card" in classes else ""
    boutons = "".join(f'<a class=" no-link" role="button" aria-label="{b}" tabindex="0">{b}</a>' for b in txt[3])
    def champ(v): return f'<span class="fieldval"><span class="fieldtext">{v}</span></span>'
    return (f'<div id="ct-{uid}" class=" dynamicbloc-contentwrapper bloc-teaser cmsorigin-maincontent">'
            f'<div class="dynamiccontentbloc"><div class="bloc-content"><div class="content-wrapper {classes}">'
            f'<div class="picture-wrapper picture-wrapper"><img class="picture " loading="lazy" src="{img}" alt="{txt[1]}"></div>'
            f'<div class="text-wrapper text-wrapper{card}"><h2 class="bloc-title bloc-title">'
            f'<span class="pretitle bloc-accent pretitle bloc-accent">{champ(txt[0])}</span>'
            f'<span class="bloctitle bloctitle">{champ(txt[1])}</span></h2>'
            f'<div class="description description">{champ(txt[2])}</div>'
            f'<div class="itembloccontentactions">{boutons}</div></div></div></div></div>'
            f'<div class="iw-clearfix"></div><style>{css_gabarit.replace("##contentid", "#ct-" + uid)}</style></div>')

def demo(css, js, autonome):
    gab = json.loads((RACINE / "gabarit" / "base.json").read_text(encoding="utf-8"))["customCSS"]
    gab = re.sub(r"/\*.*?\*/", "", gab, flags=re.S)
    blocs = []
    for n, (mep, legende) in enumerate(MISES_EN_PAGE, 1):
        blocs.append(f'<p class="legende">Bloc {n} : {legende}</p>' + bloc_inwink(n, mep, TEXTES_DEMO[n - 1], IMAGES_DEMO[n - 1], gab))
    cat = {fam: [[e[0], e[1], e[4], e[5]] for e in liste] for fam, _, liste in FAMILLES}
    cat["conflits"] = [[sorted(a), sorted(b), r] for a, b, r in CONFLITS]
    t = (RACINE / "demo" / "template.html").read_text(encoding="utf-8")
    t = t.replace("{{VERSION}}", VERSION).replace("{{BLOCS}}", "\n".join(blocs)).replace("{{CATALOGUE}}", json.dumps(cat, ensure_ascii=False))
    if autonome:
        t = t.replace("{{CSS}}", f"<style>\n{css}</style>").replace("{{JS}}", f"<script>\n{js}</script>")
    else:
        t = t.replace("{{CSS}}", '<link rel="stylesheet" href="../txim.css">').replace("{{JS}}", '<script src="../txim.js"></script>')
    return t

def catalogue_md():
    l = [f"# Catalogue txim v{VERSION}", "", "Fichier généré par `build.py` : ne pas modifier à la main.", ""]
    titres = {"image": "Animation de l'image", "texte": "Animation du texte", "survol": "Effet au survol"}
    for fam, lettre, liste in FAMILLES:
        l += [f"## {titres[fam]}", "", "| Classe | Effet | Description | JS |", "|---|---|---|---|"]
        l += [f"| `txim-{lettre}-{e[0]}` | {e[1]} | {e[4]} | {'requis' if e[5] else 'non'} |" for e in liste]
        l.append("")
    l += ["## Options", "", "| Champ du gabarit | Valeur | Classe |", "|---|---|---|"]
    for cle, fr, en, es, valeurs in OPTIONS:
        l += [f"| {fr} | {v[1]} | {'`' + v[4] + '`' if v[4] else '(aucune)'} |" for v in valeurs]
    l += ["", "## Combinaisons déconseillées", ""]
    l += [f"- {', '.join('`txim-' + x + '`' for x in sorted(a))} avec {', '.join('`txim-' + x + '`' for x in sorted(b))} : {r}." for a, b, r in CONFLITS]
    return "\n".join(l) + "\n"

# ---------------------------------------------------------------- build
def build():
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST / "demo").mkdir(parents=True)
    core = developper((SRC / "core.css").read_text(encoding="utf-8"))
    js = entete("JS optionnel : mode apparition, repli Firefox, survols Inclinaison et Projecteur") + \
         developper((SRC / "core.js").read_text(encoding="utf-8"))
    effets = {}
    for fam, lettre, liste in FAMILLES:
        for e in liste:
            effets[(fam, lettre, e)] = developper((SRC / "effets" / fam / f"{e[0]}.css").read_text(encoding="utf-8"))
    tout = entete("bibliothèque complète") + core + "".join(f"\n/* ===== {f} : {e[1]} (.txim-{l}-{e[0]}) ===== */\n" + c
                                                              for (f, l, e), c in effets.items())
    (DIST / "txim.css").write_text(tout, encoding="utf-8")
    (DIST / "txim.js").write_text(js, encoding="utf-8")
    for (fam, lettre, e), c in effets.items():
        d = DIST / "standalone" / f"{fam}-{e[0]}"
        d.mkdir(parents=True)
        (d / f"txim-{fam}-{e[0]}.css").write_text(entete(f"{fam} : {e[1]} (autonome, noyau inclus)") + core + "\n" + c, encoding="utf-8")
        (d / "txim.js").write_text(js, encoding="utf-8")
        (d / "LISEZMOI.txt").write_text(
            f"Effet {fam} « {e[1]} » : classe txim-{lettre}-{e[0]} sur le bloc (#ct-…) ou sur .content-wrapper.\n"
            f"{e[4]}\n\nCSS : txim-{fam}-{e[0]}.css (noyau inclus).\n"
            + ("JS : txim.js OBLIGATOIRE pour cet effet.\n" if e[5] else
               "JS : txim.js uniquement pour le mode « joué à l'apparition » (classe txim-apparition).\n"), encoding="utf-8")
    (DIST / "gabarit").mkdir()
    (DIST / "gabarit" / "bloc-texte-image-txim.json").write_text(json.dumps(bloc_complet(), ensure_ascii=False, indent="\t"), encoding="utf-8")
    (DIST / "demo" / "index.html").write_text(demo(tout, js, False), encoding="utf-8")
    (DIST / "demo" / "demo-autonome.html").write_text(demo(tout, js, True), encoding="utf-8")
    (RACINE / "CATALOGUE.md").write_text(catalogue_md(), encoding="utf-8")
    z = DIST / f"txim-v{VERSION}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        for p in DIST.rglob("*"):
            if p.is_file() and p != z: f.write(p, p.relative_to(DIST))
    n = sum(len(l) for _, _, l in FAMILLES)
    print(f"txim v{VERSION} : {n} effets, {len(tout)//1024} Ko de CSS, {len(js)//1024} Ko de JS -> {DIST}")

if __name__ == "__main__":
    build()
