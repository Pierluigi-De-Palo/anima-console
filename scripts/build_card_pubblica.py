#!/usr/bin/env python3
"""Da una card interna (col seriale) ai file pubblici della card. Nessun segreto esce.

COSA FA
    Legge un `card-NNN.json` di KIROSHI (che contiene seriale, impronta e nome) e
    scrive i due file che vanno in rete:

      docs/anima/verifica/dati/<ID>.json   il dato pubblico letto dalla pagina
      docs/v/<ID>/index.html               la rotta corta stampata sul QR

    Stampa a schermo il CODICE DI INGRESSO della card: è quello che il giocatore
    manderà al Direttore per farsi registrare. Non finisce in nessun file.

PERCHE' ESISTE
    Prima questi file si scrivevano a mano, uno per card. Con dieci card in arrivo
    (e con un campo crittografico da calcolare) a mano si sbaglia. Qui la lista dei
    campi ammessi e' una WHITELIST: se un giorno la card interna guadagna un campo
    nuovo, quel campo NON finisce in rete per distrazione.

LE DUE IMPRONTE, E PERCHE' SONO DUE
    verifica_ingresso  = sha256("carta|<ID>|<seriale>")     -> PUBBLICA, nel JSON
    codice di ingresso = sha256("ingresso|<ID>|<seriale>")  -> NON pubblicata

    La prima serve alla pagina per riconoscere il codice che il giocatore digita,
    senza che il seriale sia mai in rete. La seconda e' la prova che il giocatore
    ha davvero la card in mano: se fosse la stessa della prima, chiunque potrebbe
    leggerla dal JSON e spacciarsi per il titolare. Prefissi diversi = impronte
    scorrelate: da una non si risale all'altra.

PERCHE' UN SHA-256 SEMPLICE BASTA
    Il seriale e' HMAC-SHA256 troncato a 12 caratteri base32 = 60 bit di entropia
    (`sigillo.py`). Non e' una password scelta da una persona: non sta in nessun
    dizionario e non si indovina. Provarli tutti significa 2^60 tentativi.
    ⚠️ Se un giorno il seriale si accorcia o diventa leggibile a mente, questa
    assunzione cade e qui va messa una derivazione lenta (PBKDF2).

USO
    python3 scripts/build_card_pubblica.py ../kiroshi-interno/SIGILLO/card-000.json
    python3 scripts/build_card_pubblica.py ../kiroshi-interno/SIGILLO/card-*.json

— creato da SQUELCH, 2026-08-06
"""
import hashlib
import json
import os
import re
import sys

# I soli campi che possono uscire in rete. Tutto il resto della card interna
# (seriale, impronta, nome_anima, url_qr) resta dove sta.
# `cerchio` è entrato il 06/08 per decisione del Direttore: la card dice «00/10 ·
# cerchio 1», così il primo cerchio resta di 10 e i prossimi restano possibili.
CAMPI_PUBBLICI = ("card_id", "numero", "totale", "cerchio", "stato", "emessa", "collaudo")

QUI = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(os.path.dirname(QUI), "docs")

PAGINA = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Verifica card {cid} — IL SIGILLO · SYSTEMA 77</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/anima/verifica/verifica.css">
</head>
<body data-base="/anima/verifica/" data-card-id="{cid}">

  <div class="testa">
    <span class="marchio">SYSTEMA 77</span>
    <span class="etich">verifica card</span>
  </div>

  <div class="pannello" id="pannello">
    <div class="esito">
      <div class="marchio-b">◉</div>
      <div>
        <div class="l">esito verifica</div>
        <div class="v" id="esito">…</div>
      </div>
    </div>

    <span class="pill" id="pill">…</span>

    <div class="dati">
      <div><span>ID card</span><b id="id">—</b></div>
      <div><span>numero</span><b id="num">—</b></div>
      <div><span>emessa</span><b id="data">—</b></div>
    </div>

    <a class="entra" id="entra" href="/anima/dashboard/" hidden>entra nella tua area</a>
  </div>

  <div class="nota">
    <b>Che cosa dichiara questa verifica</b>
    Dichiara che questa card è autentica — cioè emessa da SYSTEMA 77 e non contraffatta.
    Non esprime alcun giudizio sulla persona che la porta.
  </div>

  <div class="nota">
    <b>Che cosa non c'è in questa pagina</b>
    Nessun nome, nessuna mail, nessun telefono, nessun indirizzo. Solo l'identificativo
    della card, il suo stato e l'esito. I dati della persona stanno dietro il suo consenso,
    non in un indirizzo che chiunque può scansionare.
  </div>

  <div class="nota warn" id="collaudo" hidden>
    <b>Card di collaudo</b>
    Questa card è stata generata con il segreto di collaudo: non è valida in produzione.
  </div>

<script src="/anima/verifica/verifica.js"></script>
</body>
</html>
<!-- generato da scripts/build_card_pubblica.py — non modificare a mano -->
"""


def normalizza(seriale: str) -> str:
    """Stessa normalizzazione del browser: maiuscolo, via trattini e spazi.

    Serve perche' il giocatore digita il codice come gli pare — con o senza
    trattini, in minuscolo, con uno spazio di troppo. L'impronta deve venire
    uguale in tutti i casi. `area.js` fa esattamente questa operazione.
    """
    return re.sub(r"[^A-Z0-9]", "", seriale.upper())


def impronta(prefisso: str, card_id: str, seriale: str) -> str:
    return hashlib.sha256(
        f"{prefisso}|{card_id}|{normalizza(seriale)}".encode()
    ).hexdigest()


def codice_ingresso(card_id: str, seriale: str) -> str:
    """Le prime 8 cifre esadecimali, in due gruppi: si detta al telefono."""
    grezzo = impronta("ingresso", card_id, seriale)[:8].upper()
    return f"{grezzo[:4]}-{grezzo[4:]}"


def costruisci(percorso: str) -> str:
    with open(percorso, encoding="utf-8") as fh:
        interna = json.load(fh)

    cid = interna["card_id"]
    seriale = interna["seriale"]

    pubblica = {c: interna[c] for c in CAMPI_PUBBLICI if c in interna}
    pubblica["verifica_ingresso"] = impronta("carta", cid, seriale)

    # Rete di sicurezza: se un campo segreto finisse qui dentro per una svista
    # futura, meglio fermarsi ora che scoprirlo online.
    testo = json.dumps(pubblica, ensure_ascii=False)
    for campo in ("seriale", "impronta", "nome_anima"):
        valore = interna.get(campo)
        if valore and str(valore) in testo:
            raise SystemExit(f"⛔ FERMO: «{campo}» sta finendo nel file pubblico di {cid}")

    dati = os.path.join(DOCS, "anima", "verifica", "dati", f"{cid}.json")
    with open(dati, "w", encoding="utf-8") as fh:
        json.dump(pubblica, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    corta = os.path.join(DOCS, "v", cid)
    os.makedirs(corta, exist_ok=True)
    with open(os.path.join(corta, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(PAGINA.format(cid=cid))

    print(f"◉ {cid}")
    print(f"   dato pubblico   docs/anima/verifica/dati/{cid}.json")
    print(f"   rotta corta     docs/v/{cid}/index.html")
    print(f"   QR da stampare  https://cyberboomer.io/v/{cid}/")
    print(f"   CODICE DI INGRESSO atteso: {codice_ingresso(cid, seriale)}")
    if interna.get("collaudo"):
        print("   ⚠  card di COLLAUDO: non valida in produzione")
    return cid


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for percorso in sys.argv[1:]:
        costruisci(percorso)
    print("\nIl codice di ingresso non è scritto in nessun file: è qui e basta.")
    print("Serve a te per riconoscere chi ti scrive «sono entrato».")
    return 0


if __name__ == "__main__":
    sys.exit(main())
