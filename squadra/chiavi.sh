#!/bin/bash
# COSA FA — la casa delle chiavi API: mette e legge segreti nel Portachiavi di
#   macOS con nomi `systema77.<servizio>`. Il valore lo CHIEDE lui, a schermo
#   spento: non passa mai dalla riga di comando, quindi non entra nella history.
#   Con `--appunti` lo prende dagli appunti e li pulisce subito dopo.
#
# ⚠️ PERCHE' CHIEDE INVECE DI LEGGERE GLI APPUNTI — incidente del 31/08. La
#   versione precedente leggeva solo `pbpaste`, e a chi la usava sembrava che
#   dovesse chiedere. Risultato: la frase di sblocco e' stata incollata come
#   COMANDO, zsh ha risposto «command not found» e il segreto e' finito in
#   chiaro in ~/.zsh_history. Un attrezzo che non chiede quello che gli serve
#   invita a darglielo per la strada sbagliata: il difetto e' dell'attrezzo.
# PERCHÉ ESISTE — le chiavi giravano per appunti e memoria: nessuna casa, un
#   arretrato di richieste mai evase (Worker coda fermo dal 01/08 per un token
#   mai consegnato; ANTHROPIC_API_KEY mai messa nei Secrets). La casa è il
#   Portachiavi; l'elenco vive in ROOT_CLODE/comuni/REGISTRO-CHIAVI.md — nomi e
#   stati, MAI valori.
# FIN DOVE ARRIVA — gestisce il Portachiavi locale del Mac. I segreti delle
#   automazioni (GitHub Actions, Cloudflare env) si mettono nelle loro sedi: qui
#   al massimo li custodisci prima di copiarli là. Nessun nome di servizio è
#   cablato: il registro sul Mac è l'unico elenco.
# USO — dal Mac:
#   bash chiavi.sh setta <servizio>   # CHIEDE la frase, a schermo spento
#   bash chiavi.sh setta <servizio> --appunti   # la prende dagli appunti
#   bash chiavi.sh leggi <servizio>   # stampa il valore (per gli script:
#                                     #   CHIAVE=$(bash chiavi.sh leggi open-meteo))
#   bash chiavi.sh lista              # le righe del registro (mai valori)
#   bash chiavi.sh cancella <servizio> # la toglie dal Portachiavi
#   Collaudo senza Mac: CHIAVI_PROVA=1 usa un portachiavi finto su file e legge
#   il valore da $CHIAVE_PROVA invece che dagli appunti.
# — creato da SQUELCH su dispatch D.R.A.G.O., 2026-08-19 (macOS bash 3.2 ok)

set -u
PREFISSO="systema77."
# Il registro si CERCA, non si deduce. La versione precedente calcolava
# `<cartella dello script>/../..`, dando per scontato che lo script vivesse in
# ROOT_CLODE/<clone>/squadra/. Scaricato sciolto dentro ROOT_CLODE puntava a
# /Users/<tu>/comuni/ — un posto che non esiste — e diceva «registro non
# trovato» quando il registro era li' a due passi. Ora risale le cartelle da
# dove sei e da dove sta lo script, e si ferma alla prima che lo contiene.
trova_registro(){
  d="$1"
  while [ -n "$d" ] && [ "$d" != "/" ]; do
    [ -f "$d/comuni/REGISTRO-CHIAVI.md" ] && { printf '%s' "$d/comuni/REGISTRO-CHIAVI.md"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}
REGISTRO="${REGISTRO:-$(trova_registro "$PWD" || trova_registro "$(cd "$(dirname "$0")" && pwd)" || echo "")}"
[ -n "$REGISTRO" ] || REGISTRO="(nessun comuni/REGISTRO-CHIAVI.md trovato risalendo da qui)"
PROVA="${CHIAVI_PROVA:-}"
FINTO="${TMPDIR:-/tmp}/portachiavi-finto-prova.txt"

muori(){ echo "✗ $*" >&2; exit 1; }

prendi_appunti(){
  if [ -n "$PROVA" ]; then
    [ -n "${CHIAVE_PROVA:-}" ] || muori "modalità prova: metti il valore in \$CHIAVE_PROVA"
    printf '%s' "$CHIAVE_PROVA"
  else
    command -v pbpaste >/dev/null || muori "pbpaste non trovato: questo comando vive sul Mac"
    pbpaste
  fi
}

chiedi(){
  # A schermo spento, e da /dev/tty: cosi' funziona anche se lo script e'
  # arrivato da una pipe, e il valore non passa mai da un argomento.
  if [ -n "$PROVA" ]; then
    [ -n "${CHIAVE_PROVA:-}" ] || muori "modalità prova: metti il valore in \$CHIAVE_PROVA"
    printf '%s' "$CHIAVE_PROVA"; return 0
  fi
  [ -t 0 ] || [ -e /dev/tty ] || muori "non c'e' un terminale per chiedere: usa --appunti"
  printf 'frase o chiave per «%s» (non si vede mentre scrivi): ' "$1" > /dev/tty
  stty -echo < /dev/tty 2>/dev/null
  IFS= read -r v < /dev/tty
  stty echo < /dev/tty 2>/dev/null
  printf '\n' > /dev/tty
  printf '%s' "$v"
}

# La FORMA si controlla prima di custodire, non dopo. Lezione del 30/08: una
# chiave con due a capo e tredici caratteri cirillici e' stata accettata da
# tutti, e ha rotto il mascheramento dei log di un repo pubblico. Qui non si
# stampa mai il valore — solo cosa non va e in che posizione.
controlla_forma(){
  v="$1"; problemi=""
  # Gli a capo si CONTANO. La prima versione li cercava con
  # `case $v in *"$(printf '\n')"*)` — ma $( ) mangia gli a capo finali, quindi
  # il modello diventava la stringa vuota e combaciava con TUTTO: bocciava
  # anche i valori sani. Trovato al primo collaudo, ed e' il motivo per cui il
  # collaudo si fa prima di consegnare.
  acapo="$(printf '%s' "$v" | LC_ALL=C tr -cd '\n\r' | wc -c | tr -d ' ')"
  [ "$acapo" -gt 0 ] && problemi="$problemi
  · contiene $acapo a capo (quasi sempre: incollato un blocco intero)"
  [ "$v" != "$(printf '%s' "$v" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')" ] &&
    problemi="$problemi
  · ha spazi all'inizio o alla fine"
  n="$(printf '%s' "$v" | LC_ALL=C tr -d '\40-\176\n\r' | wc -c | tr -d ' ')"
  [ "$n" -gt 0 ] && problemi="$problemi
  · $n caratteri non ASCII stampabili (cirillico al posto del latino? accenti?)"
  [ -z "$problemi" ] && return 0
  echo "✗ il valore e' malformato. Non lo custodisco: custodirei l'errore." >&2
  echo "$problemi" >&2
  echo "" >&2
  echo "  Ricopialo dalla fonte col tasto Copia, mai a mano, e riprova." >&2
  return 1
}

pulisci_appunti(){
  [ -n "$PROVA" ] && return 0
  printf '' | pbcopy
}

setta(){
  servizio="${1:-}"; [ -n "$servizio" ] || muori "uso: chiavi.sh setta <servizio> [--appunti]"
  da_appunti=""
  [ "${2:-}" = "--appunti" ] && da_appunti=1
  if [ -n "$da_appunti" ]; then
    valore="$(prendi_appunti)"
    [ -n "$valore" ] || muori "gli appunti sono vuoti: copia prima la chiave"
  else
    valore="$(chiedi "$servizio")"
    [ -n "$valore" ] || muori "non hai scritto niente"
  fi
  controlla_forma "$valore" || exit 1
  if [ -n "$PROVA" ]; then
    grep -v "^${PREFISSO}${servizio}	" "$FINTO" 2>/dev/null > "$FINTO.n" || true
    printf '%s\t%s\n' "${PREFISSO}${servizio}" "$valore" >> "$FINTO.n"
    mv "$FINTO.n" "$FINTO"; chmod 600 "$FINTO"
  else
    security add-generic-password -U -a "$USER" -s "${PREFISSO}${servizio}" -w "$valore" \
      || muori "il Portachiavi ha rifiutato"
  fi
  if [ -n "$da_appunti" ]; then pulisci_appunti; nota=" · appunti puliti"; else nota=""; fi
  echo "✓ ${PREFISSO}${servizio} nel Portachiavi${nota}"
  # Conferma verificabile senza stampare il valore: se e' entrato storto, si
  # vede subito invece di scoprirlo il giorno in cui la porta non si apre.
  rileggi="$(leggi "$servizio" 2>/dev/null || true)"
  if [ "$rileggi" = "$valore" ]; then
    echo "  riletto dal Portachiavi: combacia (${#valore} caratteri)"
  else
    echo "  ⚠ riletto dal Portachiavi: NON combacia. Riprova." >&2
  fi
  if [ -f "$REGISTRO" ]; then
    if ! grep -q "${PREFISSO}${servizio}" "$REGISTRO"; then
      printf '| %s | (a cosa serve?) | Portachiavi macOS (`%s%s`) | (chi la usa?) | attiva | %s |\n' \
        "$servizio" "$PREFISSO" "$servizio" "$(date +%Y-%m-%d)" >> "$REGISTRO"
      echo "✓ riga aggiunta al registro: completa «a cosa serve» e «chi la usa»"
    fi
  else
    echo "· registro non trovato ($REGISTRO): aggiungi tu la riga, senza il valore"
  fi
}

leggi(){
  servizio="${1:-}"; [ -n "$servizio" ] || muori "uso: chiavi.sh leggi <servizio>"
  if [ -n "$PROVA" ]; then
    riga="$(grep "^${PREFISSO}${servizio}	" "$FINTO" 2>/dev/null || true)"
    [ -n "$riga" ] || muori "${PREFISSO}${servizio}: non nel portachiavi finto"
    printf '%s\n' "${riga#*	}"
  else
    security find-generic-password -s "${PREFISSO}${servizio}" -w \
      || muori "${PREFISSO}${servizio}: non nel Portachiavi (chiavi.sh setta ${servizio}?)"
  fi
}

cancella(){
  servizio="${1:-}"; [ -n "$servizio" ] || muori "uso: chiavi.sh cancella <servizio>"
  if [ -n "$PROVA" ]; then
    grep -v "^${PREFISSO}${servizio}	" "$FINTO" 2>/dev/null > "$FINTO.n" || true
    mv "$FINTO.n" "$FINTO" 2>/dev/null || true
  else
    security delete-generic-password -s "${PREFISSO}${servizio}" >/dev/null 2>&1 \
      || muori "${PREFISSO}${servizio}: non c'era niente da cancellare"
  fi
  echo "✓ ${PREFISSO}${servizio} rimossa dal Portachiavi"
  echo "  (il registro non lo tocco: la riga la togli tu, e' un tuo elenco)"
}

lista(){
  if [ -n "$PROVA" ]; then
    [ -f "$FINTO" ] && cut -f1 "$FINTO" || echo "(portachiavi finto vuoto)"
  elif [ -f "$REGISTRO" ]; then
    grep '^|' "$REGISTRO" | grep -v -- '---'
  else
    echo "registro non trovato ($REGISTRO) — la lista delle chiavi vive lì, mai qui"
  fi
}

case "${1:-}" in
  setta) shift; setta "$@";;
  cancella) shift; cancella "$@";;
  leggi) shift; leggi "$@";;
  lista) lista;;
  *) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 1;;
esac
