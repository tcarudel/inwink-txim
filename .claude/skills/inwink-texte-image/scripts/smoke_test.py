"""Test automatique de la bibliothèque TXIM.
Usage : python3 smoke_test.py <racine_du_depot> [--only i-cle,t-cle,h-cle] [--sans-navigateur]

1. Contrôles statiques : macros développées, catalogue <-> fichiers sources, cohérence du bloc JSON.
2. Navigateur (dist/demo/index.html) : chaque effet d'apparition crée des animations dont le rendu progresse
   avec le défilement (pas de valeur figée), chaque survol change le rendu, pas d'erreur JS, pas de débordement horizontal à 390 px.
3. Pour les effets passés à --only : test du mode apparition et captures dans dist/screens/.
Prérequis : pip install playwright && playwright install chromium"""
import asyncio, importlib.util, json, os, re, sys, uuid

SVG = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='800'%3E%3Cdefs%3E"
       "%3ClinearGradient id='g' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%23e8743b'/%3E%3Cstop offset='1' "
       "stop-color='%2319a979'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1200' height='800' fill='url(%23g)'/%3E"
       "%3Ccircle cx='600' cy='400' r='200' fill='%23fff' opacity='.5'/%3E%3C/svg%3E")
RENDU = ["transform", "opacity", "clip-path", "mask-image", "filter", "background-size", "background-position",
         "border-radius", "letter-spacing"]
PROPS = ["scale", "translate", "rotate", "filter", "box-shadow", "text-decoration-color", "background-color", "opacity", "clip-path"]

def args():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    only = a[a.index("--only") + 1].split(",") if "--only" in a else []
    return os.path.abspath(a[0]), only, "--sans-navigateur" in a

def statique(racine, erreurs):
    spec = importlib.util.spec_from_file_location("build", os.path.join(racine, "build.py"))
    b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
    for f in ("txim.css", "txim.js"):
        if "§" in open(os.path.join(racine, "dist", f), encoding="utf-8").read():
            erreurs.append(f"macro non développée dans dist/{f}")
    effets = []
    for fam, lettre, liste in b.FAMILLES:
        cles = [e[0] for e in liste]
        if len(cles) != len(set(cles)): erreurs.append(f"clé en double dans {fam}")
        fichiers = {f[:-4] for f in os.listdir(os.path.join(racine, "src", "effets", fam)) if f.endswith(".css")}
        for c in set(cles) - fichiers: erreurs.append(f"{fam}/{c} : au catalogue mais sans fichier source")
        for c in fichiers - set(cles): erreurs.append(f"{fam}/{c}.css : fichier source absent du catalogue")
        effets += [(fam, lettre, e) for e in liste]
    g = json.load(open(os.path.join(racine, "dist", "gabarit", "bloc-texte-image-txim.json"), encoding="utf-8"))
    p = g["properties"]; fields = {f["key"]: f for f in p["itemDefinition"]["fields"]}
    regles = p["template"]["conditionalClasses"]
    for cls, conds in regles.items():
        for c in conds:
            f = fields.get(c["name"])
            if not f: erreurs.append(f"règle {cls} : champ {c['name']} inexistant"); continue
            if f["type"] == "selectlist" and c["val"] not in {v["key"] for v in f["valuesList"]}:
                erreurs.append(f"règle {cls} : valeur {c['val']} absente de {c['name']}")
    for fam, lettre, e in effets:
        if f"txim-{lettre}-{e[0]}" not in regles: erreurs.append(f"txim-{lettre}-{e[0]} : pas de règle dans le bloc JSON")
    if set(fields) != set(p["itemDefinition"]["scopes"]): erreurs.append("scopes et champs du bloc JSON ne correspondent pas")
    for cle, val in p["data"].items():
        f = fields.get(cle)
        if f and f["type"] == "selectlist" and val is not None and val not in {v["key"] for v in f["valuesList"]}:
            erreurs.append(f"data.{cle} = {val} : valeur absente de la liste")
    ids = [g["id"]] + [a["id"] for a in g["actions"]]
    try: [uuid.UUID(i) for i in ids]
    except ValueError: erreurs.append("identifiants du bloc JSON non conformes (UUID attendu)")
    print(f"Statique : {len(effets)} effets, {len(fields)} champs, {len(regles)} règles")
    return effets

async def navigateur(racine, effets, only, erreurs):
    from playwright.async_api import async_playwright
    page = "file://" + os.path.join(racine, "dist", "demo", "index.html")
    ecrans = os.path.join(racine, "dist", "screens"); os.makedirs(ecrans, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for largeur in (1400, 390):
            pg = await b.new_page(viewport={"width": largeur, "height": 900})
            pg.on("pageerror", lambda e: erreurs.append("JS : " + str(e)))
            await pg.goto(page)
            await pg.evaluate(f"document.querySelectorAll('img.picture').forEach(i=>i.src=\"{SVG}\")")
            await pg.add_style_tag(content=".pan,.ligne{display:none!important}")
            async def regler(**kw):
                js = ";".join(f"document.getElementById('{k}').value='{v}'" for k, v in kw.items())
                await pg.evaluate(js + ";document.getElementById('image').dispatchEvent(new Event('change'))")
            async def aller(n, frac):
                await pg.evaluate(f"(()=>{{const c=document.querySelectorAll('.bloc-teaser')[{n}];"
                                  f"scrollTo(0,c.getBoundingClientRect().top+scrollY-innerHeight*{frac})}})()")
                await pg.wait_for_timeout(120)
            for fam, lettre, e in effets:
                cle, cls, sel = f"{lettre}-{e[0]}", f"txim-{lettre}-{e[0]}", fam
                vide = {"image": "", "texte": "", "survol": "", "mode": "", "seuil": "txim-seuil-50"}
                vide[sel] = cls
                await regler(**vide)
                if lettre != "h":
                    await aller(0, 0.42)
                    n = await pg.evaluate("document.querySelector('.content-wrapper').getAnimations({subtree:true}).length")
                    if n == 0: erreurs.append(f"{cls} ({largeur} px) : aucune animation")
                    if largeur == 1400 and n:
                        rendu = ("(()=>{const cw=document.querySelector('.content-wrapper');const out=[];"
                                 "for(const el of [cw,...cw.querySelectorAll('*')]){for(const ps of [null,'::after']){"
                                 f"const s=getComputedStyle(el,ps);out.push({json.dumps(RENDU)}.map(p=>s.getPropertyValue(p)).join(';'))}}}}"
                                 "return out.join('#')})()")
                        r1 = await pg.evaluate(rendu); await aller(0, 0.36); r2 = await pg.evaluate(rendu)
                        if r1 == r2: erreurs.append(f"{cls} : le rendu ne progresse pas avec le défilement (valeur figée ?)")
                        await aller(0, 0.42)
                    if largeur == 390:
                        w = await pg.evaluate("document.documentElement.scrollWidth")
                        if w > 390: erreurs.append(f"{cls} : débordement horizontal sur mobile ({w} px)")
                    elif cle in only:
                        for n_bloc in (0, 1, 2):
                            await aller(n_bloc, 0.42)
                            await pg.screenshot(path=os.path.join(ecrans, f"{cls}-bloc{n_bloc + 1}.png"))
                        await regler(**dict(vide, mode="txim-apparition"))
                        await aller(1, 1.2); await pg.wait_for_timeout(300)
                        await aller(1, 0.3); await pg.wait_for_timeout(2600)
                        ok = await pg.evaluate("(()=>{const c=document.querySelectorAll('.content-wrapper')[1];"
                                               "return c.hasAttribute('data-txim-vu') && getComputedStyle(c.querySelector('.bloctitle')).opacity==='1'})()")
                        if not ok: erreurs.append(f"{cls} : mode apparition non joué ou contenu masqué")
                        await pg.screenshot(path=os.path.join(ecrans, f"{cls}-apparition-fin.png"))
                elif largeur == 1400:
                    await aller(0, 0.2)
                    if e[5] and not await pg.evaluate("document.querySelector('.content-wrapper').hasAttribute('data-txim-pointeur')"):
                        erreurs.append(f"{cls} : le JS ne suit pas le pointeur")
                    etat = ("(()=>{const cw=document.querySelector('.content-wrapper');const out=[];"
                            "for(const el of [cw.querySelector('.picture-wrapper'),cw.querySelector('.picture'),cw.querySelector('.text-wrapper'),"
                            "cw.querySelector('.bloctitle'),cw.querySelector('.itembloccontentactions>*')]){if(!el)continue;"
                            f"const s=getComputedStyle(el),a=getComputedStyle(el,'::after');out.push({json.dumps(PROPS)}.map(p=>s.getPropertyValue(p)+'|'+a.getPropertyValue(p)).join(';'))}}"
                            "return out.join('#')})()")
                    await pg.mouse.move(2, 2); await pg.wait_for_timeout(900)
                    avant = await pg.evaluate(etat)
                    r = await pg.evaluate("(()=>{const r=document.querySelector('.picture-wrapper').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
                    await pg.mouse.move(r[0] + r[2] * .85, r[1] + r[3] * .2); await pg.wait_for_timeout(1300)
                    if await pg.evaluate(etat) == avant: erreurs.append(f"{cls} : le survol ne change rien")
                    if cle in only: await pg.screenshot(path=os.path.join(ecrans, f"{cls}-survol.png"))
            print(f"Navigateur {largeur} px : terminé")
            await pg.close()
        await b.close()

def main():
    racine, only, sans_nav = args()
    erreurs = []
    effets = statique(racine, erreurs)
    inconnus = set(only) - {f"{l}-{e[0]}" for _, l, e in effets}
    if inconnus: erreurs.append("--only : effets inconnus " + ", ".join(sorted(inconnus)))
    if not sans_nav: asyncio.run(navigateur(racine, effets, only, erreurs))
    if erreurs:
        print("\nÀ corriger :"); [print(" - " + e) for e in erreurs]
    else:
        print("\nRésultat : tout est correct" + (" ; captures dans dist/screens/" if only else ""))
    sys.exit(1 if erreurs else 0)

main()
