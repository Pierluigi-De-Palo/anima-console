#!/bin/bash
# COSA FA — la casa delle chiavi API: mette e legge segreti nel Portachiavi di
#   macOS con nomi `systema77.<servizio>`. Il valore entra DAGLI APPUNTI (mai
#   digitato in chiaro in un terminale che tiene la history) e gli appunti
#   vengono puliti subito dopo.
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
#   bash chiavi.sh setta <servizio>   # valore preso dagli appunti, poi puliti
#   bash chiavi.sh leggi <servizio>   # stampa il valore (per gli script:
#                                     #   CHIAVE=$(bash chiavi.sh leggi open-meteo))
#   bash chiavi.sh lista              # le righe del registro (mai valori)
#   Collaudo senza Mac: CHIAVI_PROVA=1 usa un portachiavi finto su file e legge
#   il valore da $CHIAVE_PROVA invece che dagli appunti.
# — creato da SQUELCH su dispatch D.R.A.G.O., 2026-08-19 (macOS bash 3.2 ok)

set -u
PREFISSO="systema77."
# Il registro: accanto alla radice (script in ROOT_CLODE/<clone>/squadra/).
REGISTRO="${REGISTRO:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)/comuni/REGISTRO-CHIAVI.md}"
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

pulisci_appunti(){
  [ -n "$PROVA" ] && return 0
  printf '' | pbcopy
}

setta(){
  servizio="${1:-}"; [ -n "$servizio" ] || muori "uso: chiavi.sh setta <servizio>"
  valore="$(prendi_appunti)"
  [ -n "$valore" ] || muori "gli appunti sono vuoti: copia prima la chiave"
  if [ -n "$PROVA" ]; then
    grep -v "^${PREFISSO}${servizio}	" "$FINTO" 2>/dev/null > "$FINTO.n" || true
    printf '%s\t%s\n' "${PREFISSO}${servizio}" "$valore" >> "$FINTO.n"
    mv "$FINTO.n" "$FINTO"; chmod 600 "$FINTO"
  else
    security add-generic-password -U -a "$USER" -s "${PREFISSO}${servizio}" -w "$valore" \
      || muori "il Portachiavi ha rifiutato"
  fi
  pulisci_appunti
  echo "✓ ${PREFISSO}${servizio} nel Portachiavi · appunti puliti"
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
  leggi) shift; leggi "$@";;
  lista) lista;;
  *) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 1;;
esac
