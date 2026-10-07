#!/usr/bin/env python3
"""Construit mods.tsv (lu par banc.sh) et catalogue.html à partir des clones audités.

Usage : python3 outils/construire.py [dossier-sources]   (défaut : ~/.cache/claude-mods-banc/sources)
Entrées : outils/depots.tsv (dépôt, commit audité), outils/audit.txt (sortie de auditer.sh), le classement ci-dessous.
Les droits affichés viennent de `claude plugin validate`, jamais des README.
"""
import glob, json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "claude-mods-banc", "sources")

# palier · clé (dépôt/nom si le nom est ambigu) · ce que fait le mod, en deux phrases
CLASSEMENT = [
    ("top", "anthropics/blast-radius", "Avant un rm -rf, un git reset --hard, un git clean ou un force push, il bloque la commande et montre ce qu'elle détruirait, avec Continuer et Annuler. Ses mesures sont toutes sans effet (find, du, git status, git clean -n), mais il ne connaît que ces commandes : rmdir, find -delete ou un script passent à côté."),
    ("top", "collision-guard", "Il demande confirmation avant que Claude modifie un fichier qu'une autre session a touché dans les 30 dernières minutes. La protection qui manque quand plusieurs agents travaillent sur le même dépôt."),
    ("top", "zsh-safe", "Il fait passer sous zsh les commandes écrites pour bash (globs sans résultat, = en début de mot). Supprime l'aller-retour échec, guillemets, relance sur macOS, mais l'effet est invisible tant qu'on ne compare pas."),
    ("top", "recording-mode", "/rec masque à l'écran les clés, les données personnelles et les chiffres avant un enregistrement, et refuse d'ouvrir .env et les clés SSH. Utile pour filmer une démo ou partager son écran."),
    ("top", "whats-agent-doing", "Un encadré au-dessus du prompt dit en clair ce que fait l'agent et depuis combien de temps, historique du tour dépliable. Affichage pur : ni fichier, ni réseau, ni processus."),
    ("top", "starter-mod", "Mod d'exemple de 27 lignes qui compte les lectures de fichiers, avec /readcount. Le meilleur point de départ pour écrire son premier mod (ce n'est pas un plugin publié : il se charge sans installation)."),
    ("top", "anthropics/token-weather", "Une icône météo montre le remplissage de la fenêtre de contexte au-dessus du prompt. Le plus petit mod officiel d'Anthropic (122 lignes), sans aucun droit sensible."),
    ("top", "usage-band", "Une ligne affiche le quota sur 5 h et 7 jours, le contexte et le cache, avec les heures de remise à zéro. Déclare ne lire aucun fichier et ne faire aucun appel réseau."),
    ("top", "agent-radar", "Une ligne par sous-agent en cours : depuis combien de temps il tourne, combien d'outils il a appelés, ce qu'il fait. Taillé pour les runs à plusieurs agents."),
    ("top", "changes-receipt", "Après chaque tour, un reçu liste les fichiers créés, modifiés et supprimés, en séparant réussites et échecs. Pour relire avant un commit."),
    ("top", "anthropics/replay-theater", "/replay repasse une à une les modifications du dernier tour, diff par diff. Il observe sans rien modifier."),
    ("top", "flight-recorder", "Une frise en direct des requêtes au modèle, des appels d'outils et des sous-agents. Très parlant pour comprendre ce qui se passe pendant un tour."),
    ("top", "switchboard", "Il choisit Haiku, Sonnet ou Opus pour chaque sous-agent avant son lancement, via Jev ou l'API Decisions d'OpenAI. Peut réduire la facture, à condition de configurer ces services et de surveiller le cache."),
    ("top", "rulebook-guard", "Il remplace les tirets cadratins dans la prose, demande confirmation avant commit --amend et vérifie prettier et ruff avant un push. Un exemple de règles d'équipe codées plutôt qu'écrites."),
    ("top", "notice-board", "Il affiche une annonce dans toutes les sessions du même dépôt (par exemple « CI coupée »). Pratique pour coordonner plusieurs agents ou plusieurs personnes."),
    ("top", "auto-handoff", "Il écrit un document de passation dans handoff/ avant que le contexte soit plein ou compacté. La reprise dans une nouvelle session part de là au lieu de repartir de zéro."),
    ("top", "repo-heatmap", "Une carte du dépôt, un rectangle par fichier, s'allume quand Claude lit, cherche ou modifie. Excellent pour voir où l'agent regarde."),
    ("cible", "md-preview", "Il affiche dans un panneau, rendus comme sur GitHub, les fichiers Markdown que Claude modifie. Bien pour relire de la documentation en cours d'écriture."),
    ("cible", "output-tray", "Un panneau liste les fichiers créés pendant la session, avec Ouvrir, Afficher dans le Finder et Copier le chemin. Les boutons d'ouverture supposent macOS."),
    ("cible", "context-bar", "Une barre empilée montre le contexte par catégorie, avec le nombre de tokens de chacune. Plus détaillée que token-weather, moins lisible d'un coup d'œil."),
    ("cible", "context-meter", "Une jauge montre le remplissage du contexte et le coût de la session. Simple, sans droit sensible."),
    ("cible", "mod-store", "/mods ouvre un catalogue d'environ 2 700 mods avec leurs droits, et installe en un clic. L'installation qu'il fait est réelle et permanente : elle échappe au banc."),
    ("cible", "explain-claude-mod", "/explain reformule une réponse dans un autre format : anglais simplifié normalisé (STE), schéma, page HTML ou vidéo animée. Intéressant pour fabriquer des supports pédagogiques."),
    ("cible", "where-am-i", "Un résumé en direct : objectif, ce qui est en cours, ce qui t'attend, la suite. Il appelle le modèle pour le produire, donc consomme du quota."),
    ("cible", "session-saver", "Il nomme les sessions sans titre, et /park note où tu t'es arrêté. Utile avec beaucoup de sessions ouvertes."),
    ("cible", "session-bookmarks", "/bm met une session en favori avec une note pour la retrouver. Doublon avec session-saver : en garder un."),
    ("cible", "plan-progress", "Des barres de progression du plan, par étape, au-dessus du prompt. Gros mod (3 900 lignes) qui modifie aussi la composition du prompt."),
    ("cible", "goal-meter", "Une barre de progression pour /goal, construite à partir de la liste de tâches de Claude. Recoupe plan-progress."),
    ("cible", "model-router", "Il envoie le travail des sous-agents sur Sonnet ou Haiku, en laissant la conversation principale sur son modèle. Économise, à vérifier sur un vrai chantier."),
    ("cible", "review-watch", "Une ligne par revue de code en cours (Codex ou sous-agent). Utile seulement si tu fais relire par Codex."),
    ("cible", "pr-relay", "Il surveille la PR chaque minute et relance la session quand elle est fusionnée ou relue. Il agit de lui-même : à éviter si tu veux valider chaque push."),
    ("cible", "merge-gate", "Il bloque gh pr merge tant que la CI n'est pas verte et qu'une revue Codex n'a pas tourné. Bon garde-fou si tu fusionnes depuis Claude."),
    ("cible", "HolyGrail/usage-meter", "Quota sur 5 h, à la semaine et par modèle, plus le contexte. Doublon avec usage-band, et fait un appel réseau."),
    ("cible", "hamzafer/usage-meter", "Quota sur 5 h et 7 jours en petites barres. La version la plus légère des trois, sans droit sensible."),
    ("cible", "cache-clock", "Une ligne indique combien de minutes le cache reste encore chaud. Intéressant pour les longues sessions, recoupe token-weather."),
    ("cible", "hamzafer/token-weather", "Version enrichie de token-weather, avec compte à rebours du cache. Choisir elle ou l'officielle, pas les deux."),
    ("cible", "hamzafer/replay-theater", "Copie quasi identique de la version officielle. Aucune raison de la préférer."),
    ("cible", "hamzafer/blast-radius", "Variante de l'officiel qui lit aussi les variables d'environnement. Garder l'officiel."),
    ("cible", "mod-pack", "Un pack de 9 200 lignes : Token Weather, Cache Keeper, Prompt Queue, Wait What, Blast Radius, Ship Gate. Beaucoup de code à faire confiance d'un coup, pour des mods qui existent séparément."),
    ("cible", "next-steps", "Après chaque tour, il propose 2 ou 3 prompts suivants, à choisir avec 1, 2 ou 3. Il appelle le modèle à chaque tour, ce qui coûte."),
    ("non", "browser-lanes", "Il indique quelle session tient un navigateur Playwright, et /browser clean ferme ceux qui restent. Attention : cette fermeture peut faire perdre une session de navigateur connectée."),
    ("non", "cache-keeper", "Il garde le cache chaud en envoyant une requête au modèle environ toutes les 4 minutes. Consomme le quota en continu une fois activé."),
    ("non", "mission-control", "/mission ouvre une carte en direct de l'agent principal, de ses sous-agents et de chaque appel d'outil. Puissant, mais c'est celui qui cumule le plus de droits."),
    ("non", "coral-skin", "Il redessine Claude Code en corail, encre et crème, avec des pastilles colorées selon le risque. Purement esthétique."),
    ("non", "terminal-pet", "Un crabe en pixel art réagit à ce que fait Claude, et son ventre suit le remplissage du contexte. Mignon, sans gain concret."),
    ("non", "glance", "Prochaine réunion, PR, tickets Linear et Slack sur une ligne. Exige ces comptes configurés."),
    ("non", "snake", "Un Snake dans un panneau pendant que Claude travaille. À activer soi-même, il ne s'ouvre pas tout seul."),
    ("non", "now-playing", "Le morceau Spotify en cours, avec les paroles. Pour le fun."),
    ("non", "reels", "Des YouTube Shorts dans un panneau pendant que Claude travaille. Distraction garantie."),
    ("non", "prayer-times", "Les heures de prière et le temps restant avant la suivante. Utile seulement si tu pratiques."),
    ("lemo", "lemo-core", "Le socle obligatoire de la famille lemo (11 500 lignes) : styles, numéros de message, panneau /lemo-mod. Beaucoup de code pour un écosystème fermé."),
    ("lemo", "lemo-guard", "Il arrête Claude quand un tour dépasse un temps limite, sans compter l'attente de ta réponse. Bonne idée, mais seulement dans cet écosystème."),
    ("lemo", "lemo-meter", "Contexte, quota 5 h, coût et branche git dans une barre. Doublon avec usage-band."),
    ("lemo", "lemo-journal", "Statistiques par tour, journal et classement automatique, désactivés par défaut. Pour qui aime les tableaux de bord."),
    ("lemo", "lemo-todo", "Des notes dans un panneau, résumées par Haiku après un compactage. Un bloc-notes de session."),
    ("lemo", "lemo-recap", "Un résumé de la session en trois lignes, à la demande. Il appelle le modèle à chaque résumé."),
    ("lemo", "lemo-tone", "Un mode court (trois phrases au maximum) ou « constat puis conclusion ». Un style de sortie, pas une capacité nouvelle."),
    ("lemo", "lemo-ask", "Il numérote les questions que Claude te pose dans sa fenêtre de questions. Très mineur."),
    ("lemo", "lemo-assistant", "Un sous-agent Haiku en lecture seule rédige un rapport de trois lignes. Gadget."),
    ("lemo", "lemo-watch", "Au bout de N secondes, il écrit à ta place à Claude pour demander où il en est. Ping automatique, peu utile."),
    ("lemo", "lemo-skin", "Il numérote les messages (T01, T02) et restyle l'affichage des outils. Esthétique."),
    ("lemo", "lemo-spinner", "Il remplace les mots de l'indicateur d'attente. Esthétique."),
    ("lemo", "lemo-pomodoro", "Un minuteur de concentration dans la barre. Pour travailler en pomodoro."),
    ("lemo", "lemo-voice", "Il annonce à voix haute la fin des tâches de plus de 30 secondes. Pratique si tu fais autre chose pendant que Claude travaille."),
    ("lemo", "lemo-sound", "Des sons à chaque appel d'outil et en fin de tour. Gadget."),
    ("lemo", "lemo-lot", "Il donne à Claude un outil de tirage au sort qui affiche une carte. Gadget."),
    ("lemo", "lemo-mod", "Le paquet qui installe les 16 lemo d'un coup. À éviter : mieux vaut choisir."),
]

# comment le déclencher dans le bac à sable (fichiers : LISEZMOI.txt, src/, build/, notes.txt, .env factice)
CONSIGNE = {
    "anthropics/blast-radius": "Demande : « supprime le dossier build avec rm -rf build ». Le panneau Blast Radius doit tenir la commande et lister build/a.js, b.js, c.js. Choisis Annuler pour voir le blocage.",
    "collision-guard": "Ouvre une 2e session dans le bac (cd bac-a-sable && claude) et fais modifier src/app.js par les deux. La 2e doit demander confirmation.",
    "zsh-safe": "Demande : « lance ls *.inexistant et echo =truc ». Sans le mod, zsh échoue (no matches found, truc not found) ; avec, les deux passent.",
    "recording-mode": "Tape /rec (la pastille ● REC apparaît), puis demande : « sans outil, recopie : contact jean.dupont@exemple.fr, clé sk-ant-api03-AbCd1234, revenue 1 250 000 euros ». E-mail, clé et montant s'affichent en ••• , jusque dans ton propre message. Un .env n'est pas flouté mais fermé : Claude refuse de l'ouvrir, d'où un affichage vide. /rec off pour couper.",
    "whats-agent-doing": "Demande une tâche de plusieurs étapes : « lis tous les fichiers de src et propose 3 améliorations ». Regarde l'encadré au-dessus du prompt.",
    "starter-mod": "Demande : « lis LISEZMOI.txt puis src/app.js », puis tape /readcount.",
    "anthropics/token-weather": "Fais 2 ou 3 tours (lire des fichiers, résumer). La météo du contexte apparaît au-dessus du prompt après chaque tour.",
    "usage-band": "Après la première réponse, la bande affiche 5 h, 7 j, contexte et cache. Tape /usage-band-preview pour comparer les styles.",
    "agent-radar": "Demande : « lance 2 sous-agents en parallèle : l'un résume LISEZMOI.txt, l'autre liste les fonctions de src ». Une ligne par sous-agent doit apparaître.",
    "changes-receipt": "Demande : « crée src/util.js, modifie LISEZMOI.txt et supprime notes.txt ». Le reçu apparaît en fin de tour.",
    "anthropics/replay-theater": "Fais modifier 2 fichiers, puis tape /replay et parcours les diffs.",
    "flight-recorder": "Lance une tâche avec un sous-agent, puis ouvre la frise.",
    "notice-board": "Tape /notice suivi d'un message, puis ouvre une 2e session dans le bac : l'annonce doit y apparaître.",
    "repo-heatmap": "Tape /heatmap open, puis demande à Claude de lire et chercher dans src.",
    "auto-handoff": "Tape /autohandoff. Le déclenchement réel n'arrive qu'au compactage : vérifie surtout que la commande répond.",
    "mod-store": "Tape /mods et parcours le catalogue. N'installe rien depuis le magasin : ces installations sont réelles et échappent au banc.",
    "browser-lanes": "Tape /browser pour voir l'état. N'utilise pas /browser clean.",
    "cache-keeper": "Tape /keepwarm puis coupe-le vite : chaque ping consomme du quota.",
}
ALERTE = {
    "mod-store": "Une installation lancée depuis /mods est réelle et permanente : le banc ne la désinstallera pas.",
    "cache-keeper": "Envoie une requête au modèle environ toutes les 4 minutes une fois /keepwarm actif.",
    "browser-lanes": "/browser clean ferme des navigateurs, sessions connectées comprises.",
    "mission-control": "Cumule commandes, écriture de fichiers et appels au modèle.",
    "pr-relay": "Surveille une PR GitHub et relance la session tout seul : sans PR, il n'y a rien à voir.",
    "merge-gate": "Nécessite gh et une PR : dans le bac à sable, tu verras seulement qu'il se charge.",
    "review-watch": "Nécessite Codex CLI pour être utile.",
    "switchboard": "Nécessite Jev ou l'API Decisions configurés.",
    "glance": "Nécessite Google Calendar, Linear et Slack configurés.",
    "now-playing": "Nécessite l'app Spotify ouverte.",
    "reels": "Ouvre des YouTube Shorts.",
    "next-steps": "Appelle le modèle à chaque tour.",
    "where-am-i": "Appelle le modèle pour son résumé.",
    "mod-pack": "9 200 lignes : Wait What appelle le modèle (désactivé par défaut).",
    "lemo-mod": "Installe les 16 lemo d'un coup.",
}
SURF = {"AbovePrompt": "la bande au-dessus du prompt", "Pane": "un panneau latéral (terminal large, sinon repli)", "Spinner": "l'indicateur d'attente",
        "ToolUse": "les lignes d'appels d'outils", "UserMessage": "tes messages", "AssistantMessage": "les réponses de Claude"}
FLAGS = [("cmd", r"\$\.process\.(run|spawn)"), ("réseau", r"\$\.http\.fetch"), ("écrit", r"\$\.fs\.write"),
         ("modèle", r"\$\.model\."), ("env", r"\$\.env\.get"), ("tape à ta place", r"\$\.prompt\.submit")]

depots = dict(l.rstrip("\n").split("\t") for l in open(os.path.join(ICI, "depots.tsv")) if l.strip())
audit = {}
for l in open(os.path.join(ICI, "audit.txt")):
    p, st, h, c = (l.rstrip("\n").split("\t") + ["", "", ""])[:4]
    audit[p.lstrip("./")] = (st, h, c)
paths = sorted(audit)

# marketplaces : (racine du dépôt local) -> chemin du plugin -> (nom marketplace, nom plugin, sous-dossier marketplace)
marche = {}
for m in glob.glob(os.path.join(SRC, "*", "**", ".claude-plugin", "marketplace.json"), recursive=True):
    if "node_modules" in m:
        continue
    root = os.path.dirname(os.path.dirname(m))
    j = json.load(open(m))
    for pl in j["plugins"]:
        s = pl["source"] if isinstance(pl["source"], str) else pl["source"].get("path", "")
        marche[os.path.relpath(os.path.normpath(os.path.join(root, s)), SRC)] = (j["name"], pl["name"], os.path.relpath(root, SRC))


def resolve(cle):
    nom = cle.split("/")[-1]
    hits = [p for p in paths if p.split("/")[-1] == nom or p.split("/")[-1].endswith("_" + nom)]
    if "/" in cle:
        hits = [p for p in hits if p.startswith(cle.split("/")[0])]
    assert len(hits) == 1, (cle, hits)
    return hits[0]


def code(p):
    out = ""
    for f in glob.glob(os.path.join(SRC, p, "**", "*"), recursive=True):
        if "node_modules" not in f and "/tests/" not in f and f.endswith((".ts", ".tsx", ".mjs", ".js")) and ".test." not in f:
            out += open(f, errors="ignore").read()
    return out


def lignes(p):
    return sum(1 for f in glob.glob(os.path.join(SRC, p, "**", "*"), recursive=True)
               if "node_modules" not in f and f.endswith((".ts", ".tsx", ".mjs", ".js")) for _ in open(f, errors="ignore"))


IMG = (".png", ".gif", ".jpg", ".jpeg", ".webp", ".svg")


def readme_imgs(d):
    r = os.path.join(SRC, d, "README.md")
    if not os.path.exists(r):
        return []
    out = []
    for a, b in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)|<img[^>]+src=\"([^\"]+)\"", open(r, errors="ignore").read()):
        u = a or b
        if u.startswith("http") or "badge" in u or "shields" in u:
            continue
        f = os.path.normpath(os.path.join(d, u))
        if os.path.exists(os.path.join(SRC, f)):
            out.append(f)
    return out


def images(p):
    repo = p.split("/")[0]
    spec = readme_imgs(p) if p != repo else []
    stem = p.split("/")[-1].replace("_explain-claude-mod", "explain").lower()
    for f in sorted(glob.glob(os.path.join(SRC, repo, "**", "*"), recursive=True)):
        rel = os.path.relpath(f, SRC)
        if not f.lower().endswith(IMG) or "/site/" in rel or "/.git/" in rel or "node_modules" in rel or "/.explain/" in rel:
            continue
        if stem in os.path.basename(f).lower() and rel not in spec:
            spec.append(rel)
    if p == repo or sum(1 for x in paths if x.split("/")[0] == repo) == 1:
        spec = readme_imgs(repo) + spec
    spec = list(dict.fromkeys(spec))[:4]
    return (spec, True) if spec else (readme_imgs(repo)[:1], False)


def brut(rel):
    owner, repo = rel.split("/")[0].split("_", 1)
    sha = depots[f"{owner}/{repo}"]
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/" + "/".join(rel.split("/")[1:])


data, tsv, vus = [], [], set()
for i, (palier, cle, txt) in enumerate(CLASSEMENT, 1):
    p = resolve(cle)
    assert p not in vus, p
    vus.add(p)
    st, h, c = audit[p]
    owner, repo = p.split("/")[0].split("_", 1)
    depot = f"{owner}/{repo}"
    sub = "/".join(p.split("/")[1:])
    flags = [f for f, pat in FLAGS if re.search(pat, c)]
    events = sorted({e.split("{")[0] for e in re.findall(r"[a-z]+\.[a-zA-Z]+(?:\{[^}]*\})?", h)} - {"hooks.json"})
    # source d'installation : marketplace GitHub, marketplace en sous-dossier (clone), ou chargement direct sans plugin publié
    if p in marche:
        mk, plug, mroot = marche[p]
        msub = "/".join(mroot.split("/")[1:])
        source = f"github:{depot}" if not msub else f"clone:{depot}:{msub}"
    else:
        mk, plug, source = "-", "-", f"dir:{depot}:{sub}"
    src = code(p)
    cmds = sorted(set(re.findall(r"command\.register\(\s*\{\s*name:\s*['\"`]([\w:-]+)", src)) | set(re.findall(r"on\(\s*['\"]command\.run['\"]\s*,\s*\{\s*command:\s*['\"`]([\w:-]+)", src)))
    surf = [SURF[s] for s in SURF if re.search(r"component:\s*['\"]" + s + r"['\"]", src)]
    tools = sorted(set(re.findall(r"tool:\s*['\"](\w+)['\"]", src)))
    auto = []
    if cmds:
        auto.append("Commandes : " + ", ".join("/" + k for k in cmds[:6]) + ".")
    if surf:
        auto.append("Dessine dans " + ", ".join(surf[:4]) + ".")
    if tools:
        auto.append("Intercepte les outils " + ", ".join(tools[:5]) + " : demande une action qui les utilise.")
    if not auto:
        auto.append("Rien de déclaré à déclencher : fais un ou deux tours normaux et observe l'interface.")
    test = " ".join(([CONSIGNE[cle]] if cle in CONSIGNE else []) + auto)
    nom = p.split("/")[-1].split("_", 1)[-1] if "/" not in p else p.split("/")[-1]
    if nom == "explain-claude-mod":
        nom = "explain"
    imgs, specifique = images(p)
    url_code = f"https://github.com/{depot}" + (f"/tree/{depots[depot]}/{sub}" if sub else "")
    tsv.append([str(i), cle, nom, palier, ",".join(flags) or "aucun", mk, plug, source, depot, depots[depot], test, ALERTE.get(cle, "-"), txt])
    data.append({"rang": i, "tier": palier, "cle": cle, "nom": nom, "auteur": owner, "url": url_code, "repo": f"https://github.com/{depot}",
                 "og": f"https://opengraph.githubassets.com/1/{depot}", "txt": txt, "flags": flags, "intercepte": "tool.call" in h,
                 "events": events, "loc": lignes(p), "imgs": [brut(x) for x in imgs], "img_specifique": specifique,
                 "install": f"claude plugin marketplace add {depot} && claude plugin install {plug}@{mk}" if source.startswith("github:") else ""})

assert len(data) == len(paths), (len(data), len(paths))
with open(os.path.join(RACINE, "mods.tsv"), "w") as w:
    w.write("# rang\tcle\tnom\tpalier\tdroits\tmarketplace\tplugin\tsource\tdepot\tcommit_audite\tcomment_tester\talerte\tdescription\n")
    for r in tsv:
        w.write("\t".join(s.replace("\t", " ").replace("\n", " ") for s in r) + "\n")
tpl = open(os.path.join(ICI, "catalogue.tpl.html")).read()
open(os.path.join(RACINE, "catalogue.html"), "w").write(tpl.replace("/*DATA*/[]", json.dumps(data, ensure_ascii=False)))
# Liste des 67 dans le README, entre les marqueurs MODS:DEBUT et MODS:FIN
PALIERS = {"top": "À essayer en premier", "cible": "Utiles dans un cas précis", "non": "Gadgets, coûteux ou risqués", "lemo": "Famille lemo"}
bloc, cur = [], None
for r in tsv:
    rang, cle, nom, palier, droits, mk, plug, source, depot = r[:9]
    if palier != cur:
        cur = palier
        bloc += ["", f"### {PALIERS[palier]}", "", "| # | Mod | Dépôt | Droits | Ce qu'il fait |", "| --- | --- | --- | --- | --- |"]
    extra = "" if source.startswith("github:") else (" (via clone)" if source.startswith("clone:") else " (sans installation)")
    phrase = re.split(r"(?<=[.!?])\s", r[12])[0].replace("|", "/")
    bloc.append(f"| {rang} | {nom}{extra} | [{depot}](https://github.com/{depot}) | {droits.replace(',', ', ')} | {phrase} |")
readme = os.path.join(RACINE, "README.md")
t = open(readme).read()
debut, fin = "<!-- MODS:DEBUT -->", "<!-- MODS:FIN -->"
assert debut in t and fin in t, "marqueurs MODS absents du README"
t = t[: t.index(debut) + len(debut)] + "\n" + "\n".join(bloc).strip("\n") + "\n" + t[t.index(fin):]
open(readme, "w").write(t)

print(len(data), "mods ·", sum(1 for d in data if not d["flags"]), "sans droit sensible ·", sum(1 for r in tsv if r[7].startswith("github:")), "par marketplace GitHub ·",
      sum(1 for r in tsv if r[7].startswith("clone:")), "par clone ·", sum(1 for r in tsv if r[7].startswith("dir:")), "sans installation")
