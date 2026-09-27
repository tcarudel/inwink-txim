"""Crée un ou plusieurs blocs inwink texte + image avec des identifiants neufs, sans relancer le build.
Usage : python3 nouveau_bloc.py <racine_du_depot> [nombre] [--data cle=valeur ...] [--sortie dossier]
Exemples de --data : txim-image=rideau  txim-texte=encre  txim-mode=apparition  card=true  image-position=right
Chaque bloc JSON remplace TOUT le bloc (contenu et boutons) : à coller dans « Éditer le JSON » d'un nouveau bloc."""
import copy, json, os, sys, uuid

def valeur(v):
    return {"true": True, "false": False, "null": None}.get(v, v)

def main():
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    racine = os.path.abspath(a.pop(0))
    n = int(a.pop(0)) if a and a[0].isdigit() else 1
    data, sortie = {}, os.path.join(racine, "dist", "gabarit", "blocs")
    while a:
        opt = a.pop(0)
        if opt == "--data": k, v = a.pop(0).split("=", 1); data[k] = valeur(v)
        elif opt == "--sortie": sortie = os.path.abspath(a.pop(0))
        else: sys.exit("Option inconnue : " + opt)
    modele = json.load(open(os.path.join(racine, "dist", "gabarit", "bloc-texte-image-txim.json"), encoding="utf-8"))
    fields = {f["key"]: f for f in modele["properties"]["itemDefinition"]["fields"]}
    for k, v in data.items():
        if k not in fields: sys.exit(f"Champ inconnu : {k} (champs : {', '.join(fields)})")
        f = fields[k]
        if f["type"] == "selectlist" and v is not None and v not in [x["key"] for x in f["valuesList"]]:
            sys.exit(f"Valeur {v} invalide pour {k} (valeurs : {', '.join(x['key'] for x in f['valuesList'])})")
    os.makedirs(sortie, exist_ok=True)
    for i in range(1, n + 1):
        g = copy.deepcopy(modele)
        g["id"] = str(uuid.uuid4())
        for act in g["actions"]: act["id"] = str(uuid.uuid4())
        g["properties"]["data"].update(data)
        chemin = os.path.join(sortie, f"bloc-texte-image-txim-{g['id'][:8]}.json")
        json.dump(g, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
        print(chemin)

main()
