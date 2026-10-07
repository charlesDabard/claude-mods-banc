# Banc d'essai des mods Claude Code

Tester 67 mods Claude Code un par un : chaque mod est installé dans un projet jetable, tu l'essaies dans une vraie session, puis tu le gardes ou il est désinstallé aussitôt. Ce dépôt ne contient le code d'aucun mod : il pointe vers les dépôts de leurs auteurs, à un commit audité.

Les mods sont arrivés le 1er octobre 2026 avec Claude Code 2.1.287 : des fonctions TypeScript ou JavaScript, livrées dans des plugins, qui changent le comportement et l'interface de Claude Code (bande au-dessus du prompt, panneau latéral, gardes sur les commandes). Documentation officielle : https://code.claude.com/docs/en/plugins/mods/overview

## Démarrage

Prérequis : Claude Code 2.1.287 ou plus récent (`claude --version`), git, et un terminal à part (le banc ouvre lui-même des sessions Claude Code, il ne se lance pas depuis l'intérieur d'une session).

```bash
bash banc.sh top          # les 17 mods conseillés pour commencer
bash banc.sh              # les 67, dans l'ordre du classement
```

À la première session, Claude Code demande si tu fais confiance au dossier `bac-a-sable` : l'option sélectionnée par défaut est « No, exit ». Descends sur « Yes, I trust this folder » avant de valider, sinon la session se ferme aussitôt.

Pour ménager ton quota pendant les essais, fais tourner les sessions de test sur un petit modèle : `BANC_MODELE=claude-haiku-4-5-20251001 bash banc.sh top`. Les mods s'affichent pareil, seul le modèle qui répond change.

Avant de choisir, ouvre `catalogue.html` dans un navigateur : une carte par mod, avec capture, droits, lien vers le code, recherche et filtres. Coche les mods qui t'intéressent, la commande `bash banc.sh <noms>` se compose en bas de la page.

## Ce que fait le banc, pour chaque mod

1. Il affiche ce que fait le mod, ses droits, comment le déclencher, et vérifie si son dépôt a changé depuis l'audit.
2. Il ajoute la marketplace du mod si elle manque, puis l'installe avec `--scope project` dans `bac-a-sable/`, un petit dépôt git jetable (faux code source, faux dossier `build/`, faux `.env`). Rien n'est installé ailleurs à ce stade.
3. Il ouvre Claude Code dans le bac. Le titre de l'onglet rappelle le mod en cours. Tu testes, puis tu quittes avec `/exit`.
4. Tu tranches : `1` garder installe le mod pour toi (`--scope user`, dans tous tes projets) ; `2` bof, `3` non, `4` cassé et Entrée le désinstallent tout de suite.
5. Le bac est remis à zéro avant le mod suivant. À la fin, les marketplaces ajoutées par le banc sont retirées, sauf celles dont dépend un mod gardé.

Les verdicts vont dans `resultats.tsv`. Relancer `bash banc.sh` reprend au premier mod pas encore noté.

| Commande | Effet |
| --- | --- |
| `bash banc.sh top` | un palier : `top`, `cible`, `non` ou `lemo` |
| `bash banc.sh usage-band agent-radar` | des mods précis, par nom ou par clé (colonne `cle` de `mods.tsv`) |
| `bash banc.sh --refaire` | recommence tout, l'ancien `resultats.tsv` passe en `.bak` |
| `bash banc.sh --nettoyer` | retire ce que le banc aurait laissé après un arrêt brutal |
| `CLAUDE_BIN=/chemin/claude bash banc.sh` | utiliser un autre binaire Claude Code |
| `BANC_MODELE=claude-haiku-4-5-20251001 bash banc.sh` | choisir le modèle des sessions de test |

Désinstaller plus tard un mod gardé : `claude plugin uninstall <plugin>@<marketplace>` (l'identifiant est affiché au moment de le garder).

## Les 67 mods

Classés du plus utile au moins utile pour un usage quotidien de développeur. Droits lus par `claude plugin validate` : `cmd` lance des commandes, `réseau` fait des requêtes réseau, `écrit` écrit des fichiers, `modèle` appelle le modèle (consomme ton quota), `env` lit tes variables d'environnement, `tape à ta place` envoie un prompt à Claude. « via clone » : la marketplace vit dans un sous-dossier, le banc la clone au commit audité. « sans installation » : pas de plugin publié, chargé pour une session.

<!-- MODS:DEBUT -->
### À essayer en premier

| # | Mod | Dépôt | Droits | Ce qu'il fait |
| --- | --- | --- | --- | --- |
| 1 | blast-radius (via clone) | [anthropics/claude-code-playground](https://github.com/anthropics/claude-code-playground) | cmd | Avant un rm -rf, un git reset --hard, un git clean ou un force push, il bloque la commande et montre ce qu'elle détruirait, avec Continuer et Annuler. |
| 2 | collision-guard | [nateherkai/claude-code-mods](https://github.com/nateherkai/claude-code-mods) | cmd, écrit, env | Il demande confirmation avant que Claude modifie un fichier qu'une autre session a touché dans les 30 dernières minutes. |
| 3 | zsh-safe | [HolyGrail/claude-mods](https://github.com/HolyGrail/claude-mods) | env | Il fait passer sous zsh les commandes écrites pour bash (globs sans résultat, = en début de mot). |
| 4 | recording-mode | [nateherkai/claude-code-mods](https://github.com/nateherkai/claude-code-mods) | écrit, env | /rec masque à l'écran les clés, les données personnelles et les chiffres avant un enregistrement, et refuse d'ouvrir .env et les clés SSH. |
| 5 | whats-agent-doing | [tzafrir/whats-agent-doing](https://github.com/tzafrir/whats-agent-doing) | aucun | Un encadré au-dessus du prompt dit en clair ce que fait l'agent et depuis combien de temps, historique du tour dépliable. |
| 6 | starter-mod (sans installation) | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Mod d'exemple de 27 lignes qui compte les lectures de fichiers, avec /readcount. |
| 7 | token-weather (via clone) | [anthropics/claude-code-playground](https://github.com/anthropics/claude-code-playground) | aucun | Une icône météo montre le remplissage de la fenêtre de contexte au-dessus du prompt. |
| 8 | usage-band | [JetsonChan/CC-Usage-Band](https://github.com/JetsonChan/CC-Usage-Band) | env | Une ligne affiche le quota sur 5 h et 7 jours, le contexte et le cache, avec les heures de remise à zéro. |
| 9 | agent-radar | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Une ligne par sous-agent en cours : depuis combien de temps il tourne, combien d'outils il a appelés, ce qu'il fait. |
| 10 | changes-receipt | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | cmd | Après chaque tour, un reçu liste les fichiers créés, modifiés et supprimés, en séparant réussites et échecs. |
| 11 | replay-theater (via clone) | [anthropics/claude-code-playground](https://github.com/anthropics/claude-code-playground) | aucun | /replay repasse une à une les modifications du dernier tour, diff par diff. |
| 12 | flight-recorder | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Une frise en direct des requêtes au modèle, des appels d'outils et des sous-agents. |
| 13 | switchboard | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | réseau, env | Il choisit Haiku, Sonnet ou Opus pour chaque sous-agent avant son lancement, via Jev ou l'API Decisions d'OpenAI. |
| 14 | rulebook-guard | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, env | Il remplace les tirets cadratins dans la prose, demande confirmation avant commit --amend et vérifie prettier et ruff avant un push. |
| 15 | notice-board | [HolyGrail/claude-mods](https://github.com/HolyGrail/claude-mods) | aucun | Il affiche une annonce dans toutes les sessions du même dépôt (par exemple « CI coupée »). |
| 16 | auto-handoff | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | écrit, modèle, tape à ta place | Il écrit un document de passation dans handoff/ avant que le contexte soit plein ou compacté. |
| 17 | repo-heatmap | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | cmd | Une carte du dépôt, un rectangle par fichier, s'allume quand Claude lit, cherche ou modifie. |

### Utiles dans un cas précis

| # | Mod | Dépôt | Droits | Ce qu'il fait |
| --- | --- | --- | --- | --- |
| 18 | md-preview | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, écrit, env | Il affiche dans un panneau, rendus comme sur GitHub, les fichiers Markdown que Claude modifie. |
| 19 | output-tray | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | cmd, env | Un panneau liste les fichiers créés pendant la session, avec Ouvrir, Afficher dans le Finder et Copier le chemin. |
| 20 | context-bar | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Une barre empilée montre le contexte par catégorie, avec le nombre de tokens de chacune. |
| 21 | context-meter | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Une jauge montre le remplissage du contexte et le coût de la session. |
| 22 | mod-store | [hellosverre/mod-store](https://github.com/hellosverre/mod-store) | aucun | /mods ouvre un catalogue d'environ 2 700 mods avec leurs droits, et installe en un clic. |
| 23 | explain | [Sumit189/explain-claude-mod](https://github.com/Sumit189/explain-claude-mod) | aucun | /explain reformule une réponse dans un autre format : anglais simplifié normalisé (STE), schéma, page HTML ou vidéo animée. |
| 24 | where-am-i | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | modèle | Un résumé en direct : objectif, ce qui est en cours, ce qui t'attend, la suite. |
| 25 | session-saver | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, modèle | Il nomme les sessions sans titre, et /park note où tu t'es arrêté. |
| 26 | session-bookmarks | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | cmd, écrit, modèle, env | /bm met une session en favori avec une note pour la retrouver. |
| 27 | plan-progress | [zycck/claude-mods](https://github.com/zycck/claude-mods) | cmd, écrit | Des barres de progression du plan, par étape, au-dessus du prompt. |
| 28 | goal-meter | [nateherkai/claude-code-mods](https://github.com/nateherkai/claude-code-mods) | cmd, écrit, env | Une barre de progression pour /goal, construite à partir de la liste de tâches de Claude. |
| 29 | model-router | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Il envoie le travail des sous-agents sur Sonnet ou Haiku, en laissant la conversation principale sur son modèle. |
| 30 | review-watch | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, env | Une ligne par revue de code en cours (Codex ou sous-agent). |
| 31 | pr-relay | [HolyGrail/claude-mods](https://github.com/HolyGrail/claude-mods) | cmd, env, tape à ta place | Il surveille la PR chaque minute et relance la session quand elle est fusionnée ou relue. |
| 32 | merge-gate | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, env | Il bloque gh pr merge tant que la CI n'est pas verte et qu'une revue Codex n'a pas tourné. |
| 33 | usage-meter | [HolyGrail/claude-mods](https://github.com/HolyGrail/claude-mods) | réseau | Quota sur 5 h, à la semaine et par modèle, plus le contexte. |
| 34 | usage-meter | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Quota sur 5 h et 7 jours en petites barres. |
| 35 | cache-clock | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, écrit, env | Une ligne indique combien de minutes le cache reste encore chaud. |
| 36 | token-weather | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, env | Version enrichie de token-weather, avec compte à rebours du cache. |
| 37 | replay-theater | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Copie quasi identique de la version officielle. |
| 38 | blast-radius | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, env | Variante de l'officiel qui lit aussi les variables d'environnement. |
| 39 | mod-pack | [az9713/claude-mod-pack](https://github.com/az9713/claude-mod-pack) | cmd, modèle, tape à ta place | Un pack de 9 200 lignes : Token Weather, Cache Keeper, Prompt Queue, Wait What, Blast Radius, Ship Gate. |
| 40 | next-steps | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | modèle | Après chaque tour, il propose 2 ou 3 prompts suivants, à choisir avec 1, 2 ou 3. |

### Gadgets, coûteux ou risqués

| # | Mod | Dépôt | Droits | Ce qu'il fait |
| --- | --- | --- | --- | --- |
| 41 | browser-lanes | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd | Il indique quelle session tient un navigateur Playwright, et /browser clean ferme ceux qui restent. |
| 42 | cache-keeper | [nateherkai/claude-code-mods](https://github.com/nateherkai/claude-code-mods) | écrit, modèle, env, tape à ta place | Il garde le cache chaud en envoyant une requête au modèle environ toutes les 4 minutes. |
| 43 | mission-control | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, écrit, modèle, env | /mission ouvre une carte en direct de l'agent principal, de ses sous-agents et de chaque appel d'outil. |
| 44 | coral-skin | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Il redessine Claude Code en corail, encre et crème, avec des pastilles colorées selon le risque. |
| 45 | terminal-pet | [promptadvisers/claude-mods-starter-kit](https://github.com/promptadvisers/claude-mods-starter-kit) | aucun | Un crabe en pixel art réagit à ce que fait Claude, et son ventre suit le remplissage du contexte. |
| 46 | glance | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd | Prochaine réunion, PR, tickets Linear et Slack sur une ligne. |
| 47 | snake | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Un Snake dans un panneau pendant que Claude travaille. |
| 48 | now-playing | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, réseau | Le morceau Spotify en cours, avec les paroles. |
| 49 | reels | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | cmd, réseau, env | Des YouTube Shorts dans un panneau pendant que Claude travaille. |
| 50 | prayer-times | [hamzafer/claude-code-mods](https://github.com/hamzafer/claude-code-mods) | aucun | Les heures de prière et le temps restant avant la suivante. |

### Famille lemo

| # | Mod | Dépôt | Droits | Ce qu'il fait |
| --- | --- | --- | --- | --- |
| 51 | lemo-core | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | env | Le socle obligatoire de la famille lemo (11 500 lignes) : styles, numéros de message, panneau /lemo-mod. |
| 52 | lemo-guard | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il arrête Claude quand un tour dépasse un temps limite, sans compter l'attente de ta réponse. |
| 53 | lemo-meter | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | réseau | Contexte, quota 5 h, coût et branche git dans une barre. |
| 54 | lemo-journal | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | écrit, modèle, env | Statistiques par tour, journal et classement automatique, désactivés par défaut. |
| 55 | lemo-todo | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | modèle | Des notes dans un panneau, résumées par Haiku après un compactage. |
| 56 | lemo-recap | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | modèle | Un résumé de la session en trois lignes, à la demande. |
| 57 | lemo-tone | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Un mode court (trois phrases au maximum) ou « constat puis conclusion ». |
| 58 | lemo-ask | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il numérote les questions que Claude te pose dans sa fenêtre de questions. |
| 59 | lemo-assistant | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Un sous-agent Haiku en lecture seule rédige un rapport de trois lignes. |
| 60 | lemo-watch | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | tape à ta place | Au bout de N secondes, il écrit à ta place à Claude pour demander où il en est. |
| 61 | lemo-skin | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il numérote les messages (T01, T02) et restyle l'affichage des outils. |
| 62 | lemo-spinner | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il remplace les mots de l'indicateur d'attente. |
| 63 | lemo-pomodoro | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Un minuteur de concentration dans la barre. |
| 64 | lemo-voice | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il annonce à voix haute la fin des tâches de plus de 30 secondes. |
| 65 | lemo-sound | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Des sons à chaque appel d'outil et en fin de tour. |
| 66 | lemo-lot | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Il donne à Claude un outil de tirage au sort qui affiche une carte. |
| 67 | lemo-mod | [lemomo-ai/lemo-mod](https://github.com/lemomo-ai/lemo-mod) | aucun | Le paquet qui installe les 16 lemo d'un coup. |
<!-- MODS:FIN -->

## Sécurité

Un mod n'a pas de sandbox. Il tourne avec tes droits : il peut lire et écrire tes fichiers, lancer des processus, faire des requêtes réseau, lire tes variables d'environnement et tes clés, voir et réécrire chaque prompt et chaque appel d'outil. La sandbox de Claude Code isole les commandes Bash de Claude, pas ce que lance un mod. Installer dans le bac à sable limite l'endroit où le mod est actif, pas ce qu'il peut atteindre sur ta machine.

Ce que l'audit donne :

- Chaque dépôt a été cloné au commit noté dans `outils/depots.tsv`, et chaque mod passé à `claude plugin validate`, qui lit le code sans l'exécuter. Les badges du catalogue (`cmd`, `réseau`, `écrit`, `modèle`, `env`, `tape à ta place`, `intercepte`) viennent de cette lecture, pas des README.
- Le banc compare le commit actuel de chaque dépôt au commit audité et prévient s'il a changé. L'installation se fait depuis la marketplace de l'auteur, donc sur son code actuel : un avertissement « le dépôt a changé » veut dire que ce code-là n'a pas été relu.

Ce que l'audit ne donne pas : une garantie. `validate` dit quelles API un mod appelle, pas avec quels arguments. Pour un mod qui lance des commandes ou touche au réseau, lis le code (lien « code » de chaque carte) avant de le garder.

Trois mods demandent une attention particulière, et le banc l'affiche avant de les lancer : `mod-store` (une installation faite depuis son magasin est réelle et échappe au banc), `cache-keeper` (appelle le modèle toutes les 4 minutes environ une fois `/keepwarm` actif, donc consomme ton quota), `browser-lanes` (`/browser clean` ferme des navigateurs).

## Limites connues

- Tes réglages personnels restent actifs pendant les essais (CLAUDE.md, hooks, autres plugins). Ils peuvent interférer : par exemple Claude te pose une question avant qu'un mod de garde ait eu l'occasion d'agir.
- Un garde par motif de commande ne voit que ce qu'il connaît : blast-radius retient `rm -rf` mais pas `rmdir` ni `find -delete`. C'est un filet, pas un système de permissions.
- Si tu as déjà une marketplace qui porte le même nom que celle d'un mod (par exemple `claude-mods`), le banc l'utilise telle quelle.
- `starter-mod` n'est pas un plugin publié : il se charge pour la session avec `--plugin-dir`, sans installation.
- Plusieurs mods n'ont rien à montrer sans un service configuré (PR GitHub, Codex, Jev, Spotify, Linear) : le banc le signale.
- L'arrêt par Ctrl-C pendant une session de test retire le mod en cours grâce au nettoyage de sortie ; s'il reste quelque chose, `bash banc.sh --nettoyer`.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `banc.sh` | le banc d'essai |
| `mods.tsv` | une ligne par mod : classement, droits, marketplace, commit audité, consigne de test |
| `catalogue.html` | le catalogue visuel, généré |
| `outils/depots.tsv` | les 12 dépôts sources et leur commit audité |
| `outils/auditer.sh` | clone chaque dépôt au commit audité et passe chaque mod à `claude plugin validate` |
| `outils/construire.py` | génère `mods.tsv` et `catalogue.html` depuis l'audit et le classement |
| `outils/catalogue.tpl.html` | gabarit du catalogue |

Mettre à jour après avoir changé un commit dans `outils/depots.tsv` :

```bash
bash outils/auditer.sh
python3 outils/construire.py
```

## Auteurs et licences

Ce dépôt ne redistribue aucun code de mod. Chaque mod appartient à son auteur et s'installe depuis son dépôt : anthropics/claude-code-playground, az9713/claude-mod-pack, hamzafer/claude-code-mods, hellosverre/mod-store, HolyGrail/claude-mods, JetsonChan/CC-Usage-Band, lemomo-ai/lemo-mod, nateherkai/claude-code-mods, promptadvisers/claude-mods-starter-kit, Sumit189/explain-claude-mod, tzafrir/whats-agent-doing, zycck/claude-mods. Deux d'entre eux (HolyGrail/claude-mods et Sumit189/explain-claude-mod) ne publient pas de licence au commit audité. Les captures du catalogue sont chargées depuis ces dépôts, au commit audité.
