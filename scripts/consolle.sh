#!/usr/bin/env bash
# consolle.sh — UN comando, e la consolle dietro la porta è aggiornata.
#
# A CHI SERVE. Al Direttore, che non è un programmatore e non deve ricordare
# sei comandi in ordine. Qui ce n'è uno. Tutto quello che fa lo dice in chiaro
# mentre lo fa: se qualcosa non va, si vede DOVE si è fermato.
#
#   bash scripts/consolle.sh
#
# COSA FA, nell'ordine: prende gli aggiornamenti · rigenera la porta leggendo i
# file veri di ROOT_CLODE · mette il risultato su un ramo suo · apre una PR in
# bozza. NON fonde: docs/ lo fonde il Direttore, ed è il confine di questa casa.
#
# ⚠️ LA FRASE NON PASSA MAI DA QUI. La legge build_porta.py dal Portachiavi.
#    Questo script non la vede, non la stampa e non la scrive da nessuna parte.
#    Se un giorno qualcuno aggiunge un argomento per passarla, ha rotto la
#    difesa: la history della shell è un log, e i log si leggono.
#
# — creato da SQUELCH, 2026-09-05
set -u

cd "$(dirname "$0")/.." || { echo "✗ non trovo la cartella del sito"; exit 1; }
RAMO="porta/$(date +%Y-%m-%d-%H%M)"

dì() { printf '\n\033[36m▸ %s\033[0m\n' "$1"; }
ok() { printf '  ✓ %s\n' "$1"; }
no() { printf '  ✗ %s\n' "$1"; }

dì "1/5 · prendo gli aggiornamenti"
if git pull --ff-only 2>&1 | sed 's/^/  /'; then ok "aggiornato"; else
  no "il pull non è andato liscio: guarda sopra e riprova quando è pulito"; exit 1; fi

dì "2/5 · rigenero la porta dai file veri"
# La cartella madre serve: senza, prompt e digest non si leggono e la pagina
# lo direbbe invece di riempirsi da sola. Meglio saperlo prima di pubblicare.
if [ ! -d "../comuni" ]; then
  no "non raggiungo ROOT_CLODE da qui: prompt e digest verrebbero vuoti."
  no "lancia questo comando dal Mac, dentro ~/Desktop/ROOT_CLODE/anima-console"; exit 1
fi
if ! python3 scripts/build_porta.py 2>&1 | sed 's/^/  /'; then
  no "la porta non si è rigenerata. Niente è stato pubblicato."; exit 1; fi

if git diff --quiet -- docs/index.html; then
  dì "niente da fare"; ok "la consolle è già aggiornata: nessuna modifica da mandare."; exit 0; fi

dì "3/5 · metto il lavoro su un ramo suo"
git checkout -q -b "$RAMO" || { no "non riesco a creare il ramo $RAMO"; exit 1; }
# SOLO docs/index.html, e con i due trattini: `git commit` committa l'indice
# intero, e un'altra sessione può averci messo roba mentre questo girava.
git add docs/index.html
git commit -q -m "consolle: la porta si riapre sui file di oggi

Rigenerata da scripts/build_porta.py: prompt per casa, digest, PR che
aspettano il Direttore, e il posto dei numeri.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" -- docs/index.html \
  || { no "il commit non è andato"; exit 1; }
ok "ramo $RAMO"

dì "4/5 · lo mando su GitHub"
git push -q -u origin "$RAMO" 2>&1 | sed 's/^/  /' || { no "il push non è andato"; exit 1; }
ok "spinto"

dì "5/5 · apro la richiesta, in bozza"
if command -v gh >/dev/null 2>&1; then
  URL=$(gh pr create --draft --base main --head "$RAMO" \
    --title "consolle: la porta riaperta sui file di $(date +%d/%m)" \
    --body "Rigenerata con \`bash scripts/consolle.sh\`.
Dentro c'è solo \`docs/index.html\`: **la fondi tu**, è la tua porta.
La frase di sblocco non è passata da nessuna parte." 2>&1 | tail -1)
  ok "richiesta aperta: $URL"
else
  no "gh non c'è: il ramo è su GitHub, la richiesta aprila a mano."
fi

git checkout -q - 2>/dev/null
printf '\n\033[32m◉ fatto.\033[0m Apri la richiesta qui sopra e premi «Merge».\n'
printf '  Poi cyberboomer.io mostra la consolle di oggi.\n\n'
