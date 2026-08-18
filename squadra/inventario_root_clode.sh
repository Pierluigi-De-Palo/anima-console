#!/bin/bash
# COSA FA — inventario di ROOT_CLODE in SOLA LETTURA: albero, dimensioni, date,
#   verifica dei percorsi che i repo citano come vivi, caccia allo scanner della
#   Bilancia. Non sposta, non cancella, non apre contenuti.
# PERCHÉ ESISTE — la Bilancia ha contato 377 promesse rotte in 136 documenti
#   (10/08): prima di riorganizzare per fruizione umana serve l'inventario vero,
#   non la memoria. Riorganizzare alla cieca sarebbe una riparazione finta.
# FIN DOVE ARRIVA — di RISERVATO/ riporta solo i conteggi, mai i nomi dei file;
#   dei file opachi (FORK.md, IDEE.md, ...) solo nome/dimensione/data, mai il
#   contenuto. I cloni dei repo li conta come blocchi, senza entrare in .git.
# USO — dal Mac, dentro ROOT_CLODE (o passando il percorso):
#   bash inventario_root_clode.sh [/percorso/di/ROOT_CLODE]
#   → scrive inventario-root-clode-AAAA-MM-GG.txt nella cartella corrente.
#   Poi si allega il file alla chat di D.R.A.G.O.
# — creato da SQUELCH su dispatch D.R.A.G.O., 2026-08-18 (macOS bash 3.2 ok)

set -u
RADICE="${1:-.}"
cd "$RADICE" || { echo "✗ percorso non trovato: $RADICE"; exit 1; }
OGGI=$(date +%Y-%m-%d)
OUT="$OLDPWD/inventario-root-clode-$OGGI.txt"

# I cloni dei repo: blocchi da non attraversare (né loro né i .git).
CLONI="kiroshi-fake-checker systema77-site animagame-site cyberboomer-ninja-site anima-solar-site anima-console"

dentro_clone() { # $1 = percorso relativo: 0 se sta dentro un clone
  for c in $CLONI; do case "$1" in "./$c"/*|"./$c") return 0;; esac; done
  return 1
}

{
echo "INVENTARIO ROOT_CLODE · $OGGI · $(pwd)"
echo "generato da inventario_root_clode.sh — sola lettura"
echo

echo "== 1. PRIMO LIVELLO (cartelle e file alla radice) =="
for f in * .[!.]*; do
  [ -e "$f" ] || continue
  if [ -d "$f" ]; then
    n=$(find "$f" -type f -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
    kb=$(du -sk "$f" 2>/dev/null | cut -f1)
    tipo="dir "
    echo "$tipo $f — $n file, ${kb}KB"
  else
    kb=$(du -sk "$f" 2>/dev/null | cut -f1)
    echo "file $f — ${kb}KB"
  fi
done
echo

echo "== 2. ALBERO (2 livelli, cloni esclusi, RISERVATO solo conteggio) =="
find . -maxdepth 2 -type d -not -path '*/.git*' 2>/dev/null | sort | while read -r d; do
  [ "$d" = "." ] && continue
  dentro_clone "$d" && continue
  case "$d" in ./RISERVATO/*) continue;; esac
  n=$(find "$d" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "$d ($n file diretti)"
done
echo

echo "== 3. PERCORSI CHE I REPO CITANO COME VIVI (per nome, ovunque siano) =="
# Dalla mappa delle citazioni ricostruita dai 5 repo il 18/08.
VIVI="CLAUDE.md BACHECA.md CONVENZIONE-AGENTI.md REGOLA-HTML-IN-DOCS.md
STANDARD-VISUAL.md DESIGN-SYSTEM-ANIMA-v1.md SCHEMA.md sigillo.py solco.js
PROGETTO-FALO-interazioni-cerchio.md CONTRATTO-PUNTI-v1.html
DA-JUDY-punteggio-ratificato.md worker.js PROVA-IL-SOLCO.html
ROSTER-E-CICLO.md DA-KIROSHI-per-SQUELCH-bot-slack-L1.md
DA-JUDY-ninja-blu-link.md LEGGIMI ACCORDO-CONFINE-KIROSHI.md
SCHEDA-PROFILO.md SYSTEM-77-palette.html
PROGETTO-COSTELLAZIONE-2026-08-01.md CONSOLE-SYSTEMA-77.html LICENZA-DATI.md
STILE-UNICO.md pubblica.sh"
for nome in $VIVI; do
  trovati=$(find . -maxdepth 4 -name "$nome" -not -path '*/.git/*' -not -path './RISERVATO/*' 2>/dev/null)
  if [ -n "$trovati" ]; then
    echo "TROVATO  $nome →" $trovati
  else
    echo "MANCA    $nome"
  fi
done
echo

echo "== 4. FILE OPACHI (solo nome/dimensione/data — il contenuto resta tuo) =="
for nome in FORK.md IDEE.md KIROSHI.md STATO.md APERTURA.md; do
  find . -maxdepth 3 -name "$nome" -not -path '*/.git/*' 2>/dev/null | while read -r f; do
    kb=$(du -sk "$f" | cut -f1)
    data=$(ls -l "$f" | awk '{print $6, $7, $8}')
    echo "$f — ${kb}KB — $data"
  done
done
echo

echo "== 5. CACCIA ALLO SCANNER DELLA BILANCIA (377 promesse rotte, 10/08) =="
find . -maxdepth 4 \( -name '*bilancia*' -o -name '*promesse*' -o -name '*metro*' -o -name '*scan*' \) \
  -not -path '*/.git/*' -not -path './RISERVATO/*' 2>/dev/null | head -20
echo "(vuoto = lo scanner non è in ROOT_CLODE: dirmelo è già un dato)"
echo

echo "== 6. TOCCATI NEGLI ULTIMI 30 GIORNI (fuori dai cloni) =="
find . -maxdepth 3 -type f -mtime -30 -not -path '*/.git/*' -not -path './RISERVATO/*' 2>/dev/null | while read -r f; do
  dentro_clone "$f" || echo "$f"
done | head -40
echo

echo "== 7. RISERVATO/ (solo aggregato) =="
if [ -d RISERVATO ]; then
  echo "esiste — $(find RISERVATO -type f 2>/dev/null | wc -l | tr -d ' ') file, $(du -sk RISERVATO 2>/dev/null | cut -f1)KB"
else
  echo "non esiste a questo livello"
fi
echo

echo "== 8. TOTALI =="
echo "cartelle primo livello: $(find . -maxdepth 1 -type d | wc -l | tr -d ' ')"
echo "file totali (fuori .git): $(find . -type f -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')"
echo "dimensione totale: $(du -sk . 2>/dev/null | cut -f1)KB"
} > "$OUT"

# Versione HTML per il Direttore (si apre su Brave): stesso contenuto, stile macchina.
OUT_HTML="${OUT%.txt}.html"
{
echo '<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">'
echo "<title>Inventario ROOT_CLODE · $OGGI</title>"
echo '<style>body{background:#0a0e14;color:#d7e3ef;font-family:ui-monospace,Menlo,monospace;'
echo 'font-size:13px;line-height:1.5;padding:24px}h1{color:#22d3ee;font-size:16px;letter-spacing:.1em}'
echo 'pre{white-space:pre-wrap;word-break:break-word}</style></head><body>'
echo "<h1>◉ INVENTARIO ROOT_CLODE · $OGGI</h1><pre>"
sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' "$OUT"
echo '</pre><p>— generato da inventario_root_clode.sh · sola lettura</p></body></html>'
} > "$OUT_HTML"

echo "✓ rapporto scritto: $OUT"
echo "✓ versione HTML:    $OUT_HTML"
echo "  Allegane uno alla chat di D.R.A.G.O. — da lì parte il passo B (riorganizzazione mirata)."
