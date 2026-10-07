#!/usr/bin/env bash
# Clone chaque dépôt de depots.tsv au commit audité, puis passe chaque mod à `claude plugin validate`.
# Sortie : outils/audit.txt (chemin, statut, événements, appels), lu par construire.py.
# Usage : bash outils/auditer.sh [dossier-sources]   (défaut : ~/.cache/claude-mods-banc/sources)
# Rien n'est exécuté : validate lit le code sans le lancer.
set -euo pipefail
ICI="$(cd "$(dirname "$0")" && pwd)"
SRC="${1:-${XDG_CACHE_HOME:-$HOME/.cache}/claude-mods-banc/sources}"
mkdir -p "$SRC"

while IFS=$'\t' read -r depot sha; do
	d="$SRC/${depot/\//_}"
	if [[ ! -d "$d/.git" ]]; then
		git clone -q "https://github.com/$depot" "$d"
	fi
	git -C "$d" fetch -q origin 2>/dev/null || true
	git -C "$d" checkout -q "$sha"
	echo "ok $depot @ $sha"
done <"$ICI/depots.tsv"

: >"$ICI/audit.txt"
cd "$SRC"
find . -path '*/.claude-plugin/plugin.json' -not -path '*/node_modules/*' | sed 's#/.claude-plugin/plugin.json##' | sort | while read -r p; do
	out=$(claude plugin validate "$p" 2>&1 </dev/null || true)
	st=$(grep -q 'Validation passed' <<<"$out" && echo OK || echo KO)
	h=$(grep -E ' hooks: ' <<<"$out" | sed 's/.* hooks: //' | tr '\n' ' ' || true)
	c=$(grep -E ' calls: ' <<<"$out" | sed 's/.* calls: //' | tr '\n' ' ' || true)
	# validate écrit des chemins absolus : on les rend relatifs au dossier des sources (pas de chemin personnel dans le dépôt)
	h="${h//$SRC\//}"; c="${c//$SRC\//}"
	printf '%s\t%s\t%s\t%s\n' "${p#./}" "$st" "$h" "$c" >>"$ICI/audit.txt"
done
echo "$(grep -c . "$ICI/audit.txt") mods audités, $(grep -c $'\tKO\t' "$ICI/audit.txt" || true) en échec de validation"
