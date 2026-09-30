"""Étape « Livrer » de la skill : version, changelog, build, test, commit local.
Usage : python3 livrer.py <racine_du_depot> <mineure|patch|majeure> "Entrée 1" ["Entrée 2" ...] [--sans-test] [--commit]

- Incrémente VERSION dans build.py (mineure : nouvel effet ; patch : correction ; majeure : rupture de classes).
- Ajoute une section « ## X.Y.Z » en tête de CHANGELOG.md avec les entrées données.
- Relance build.py, puis smoke_test.py (sauf --sans-test).
- --commit (Claude Code) : git add -A && git commit « txim vX.Y.Z : <entrée 1> ». Ne pousse JAMAIS :
  le push reste une décision de l'utilisateur ; la GitHub Action crée ensuite le tag vX.Y.Z et la release."""
import os, re, subprocess, sys

def main():
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    racine, niveau = os.path.abspath(a[0]), a[1]
    options = {x for x in a[2:] if x.startswith("--")}
    entrees = [x for x in a[2:] if not x.startswith("--")]
    if niveau not in ("majeure", "mineure", "patch"): sys.exit("Niveau attendu : majeure, mineure ou patch")
    if not entrees: sys.exit("Au moins une entrée de changelog est nécessaire")

    build = os.path.join(racine, "build.py")
    src = open(build, encoding="utf-8").read()
    m = re.search(r'^VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"', src, re.M)
    if not m: sys.exit("VERSION introuvable dans build.py")
    ma, mi, pa = map(int, m.groups())
    ancienne = f"{ma}.{mi}.{pa}"
    ma, mi, pa = {"majeure": (ma + 1, 0, 0), "mineure": (ma, mi + 1, 0), "patch": (ma, mi, pa + 1)}[niveau]
    nouvelle = f"{ma}.{mi}.{pa}"
    if subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/v{nouvelle}"], cwd=racine,
                      capture_output=True).returncode == 0:
        sys.exit(f"Le tag v{nouvelle} existe déjà : choisis un autre niveau.")
    open(build, "w", encoding="utf-8").write(src[:m.start()] + f'VERSION = "{nouvelle}"' + src[m.end():])

    chemin = os.path.join(racine, "CHANGELOG.md")
    cl = open(chemin, encoding="utf-8").read() if os.path.exists(chemin) else "# Changelog\n"
    section = f"## {nouvelle}\n" + "".join(f"- {e}\n" for e in entrees) + "\n"
    cl = re.sub(r"^(# Changelog\n+)", lambda x: x[1] + section, cl, count=1) if cl.startswith("# Changelog") else "# Changelog\n\n" + section + cl
    open(chemin, "w", encoding="utf-8").write(cl)
    print(f"Version : {ancienne} -> {nouvelle}")

    subprocess.run([sys.executable, "build.py"], cwd=racine, check=True)
    if "--sans-test" not in options:
        test = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smoke_test.py")
        if subprocess.run([sys.executable, test, racine], cwd=racine).returncode != 0:
            sys.exit("Test en échec : rien n'est commité. Corrige, puis relance avec le niveau « patch » "
                     "ou restaure VERSION et CHANGELOG avant de recommencer.")

    if os.path.isdir(os.path.join(racine, ".git")):
        subprocess.run(["git", "status", "--short"], cwd=racine)
        if "--commit" in options:
            subprocess.run(["git", "add", "-A"], cwd=racine, check=True)
            subprocess.run(["git", "commit", "-q", "-m", f"txim v{nouvelle} : {entrees[0]}"], cwd=racine, check=True)
            print(f"\nCommit local créé. Pour publier : git push (la GitHub Action créera le tag v{nouvelle} et la release).")
    print(f"\nLivraison prête : txim v{nouvelle}")

main()
