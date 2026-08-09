#!/usr/bin/env python3
"""IL TEST DELLE LETTERE AMBIGUE — quello che @KIROSHI aspetta per coniare SYS-02.

IL PROBLEMA CHE VERIFICA
    Il seriale stampato sul retro della card usa l'alfabeto base32 (A-Z + 2-7).
    Non ha 0/1/8/9, ma tre coppie si confondono a occhio: Z/2, S/5, G/6 — e il
    seriale della carta 0 contiene sia G sia Z. Chi legge male un carattere
    veniva respinto senza capire perche'.
    Rimedio scelto da KIROSHI (strada «b»): la pagina di login NORMALIZZA le
    confondibili prima di dire no. Cosi' non si tocca nessun seriale gia'
    stampato, e si ripara anche la carta 0 e la 1.

PERCHE' QUESTO TEST ESISTE
    Il rimedio vive in DUE posti che devono restare identici:
      - scripts/build_card_pubblica.py  (calcola l'impronta pubblicata)
      - docs/anima/dashboard/area.js    (ricalcola l'impronta nel browser)
    Se divergono, le card smettono di aprirsi e NESSUNO se ne accorge finche'
    qualcuno non prova ad entrare. Questo test confronta le due implementazioni
    facendole girare davvero, non leggendole.

    E verifica la cosa che conta di piu': che la normalizzazione NON sia troppo
    generosa. Una porta che si apre con qualunque codice e' peggio di una che
    non si apre.

USO
    python3 scripts/prova_lettere_ambigue.py
    (esce 0 se passa, 1 se no — cosi' si puo' mettere in un hook)

— creato da SQUELCH, 2026-08-09
"""
import importlib.util
import json
import os
import random
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
AREA_JS = os.path.join(RADICE, "docs", "anima", "dashboard", "area.js")

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"   # RFC 4648, quello di sigillo.py


def carica_python():
    spec = importlib.util.spec_from_file_location(
        "bcp", os.path.join(QUI, "build_card_pubblica.py"))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def normalizza_in_js(valori):
    """Fa girare DAVVERO le due funzioni di area.js, estraendole dal file vero.

    Non le riscrivo qui: se le riscrivessi, il test proverebbe la mia copia
    invece del codice che gira nel browser — cioe' non proverebbe niente.
    """
    sorgente = open(AREA_JS, encoding="utf-8").read()

    pezzi = []
    for nome, pattern in (
        ("CONFONDIBILI", r"var CONFONDIBILI = \{.*?\};"),
        ("normalizzaId", r"function normalizzaId\(t\) \{.*?\}"),
        ("normalizzaCodice", r"function normalizzaCodice\(t\) \{.*?\n  \}"),
    ):
        trovato = re.search(pattern, sorgente, re.S)
        if not trovato:
            raise SystemExit(
                f"⛔ non trovo «{nome}» in area.js — il test e' rimasto indietro "
                f"rispetto al codice, oppure il codice e' stato riscritto.")
        pezzi.append(trovato.group(0))

    script = "\n".join(pezzi) + """
const input = JSON.parse(process.argv[1]);
console.log(JSON.stringify({
  codice: input.map(normalizzaCodice),
  id: input.map(normalizzaId),
}));
"""
    fatto = subprocess.run(["node", "-e", script, json.dumps(valori)],
                           capture_output=True, text=True)
    if fatto.returncode != 0:
        raise SystemExit(f"⛔ node ha rifiutato il codice di area.js:\n{fatto.stderr}")
    return json.loads(fatto.stdout)


def seriale_finto(rng):
    grezzo = "".join(rng.choice(ALFABETO) for _ in range(12))
    return "-".join(grezzo[i:i + 4] for i in range(0, 12, 4))


def main() -> int:
    py = carica_python()
    esiti = []

    def verifica(titolo, condizione, dettaglio=""):
        esiti.append((titolo, bool(condizione), dettaglio))

    # ── 1 · le tre coppie confondibili aprono la stessa porta ──────────────────
    # Un seriale costruito apposta con tutte e tre le coppie dentro.
    vero = "GZSG-ZS62-5G2Z"
    letture_sbagliate = {
        "legge 6 dove c'e' G": vero.replace("G", "6"),
        "legge 2 dove c'e' Z": vero.replace("Z", "2"),
        "legge 5 dove c'e' S": vero.replace("S", "5"),
        "legge le lettere al posto delle cifre": vero.replace("6", "G").replace("2", "Z").replace("5", "S"),
        "minuscolo e con spazi": vero.lower().replace("-", " "),
        "tutto attaccato": vero.replace("-", ""),
    }
    atteso = py.normalizza(vero)
    for come, sbagliato in letture_sbagliate.items():
        verifica(f"chi {come} entra lo stesso",
                 py.normalizza(sbagliato) == atteso,
                 f"{sbagliato} → {py.normalizza(sbagliato)} (atteso {atteso})")

    # 0/1/8/9 non esistono in base32: chi li digita ha letto male di sicuro
    for digitato, giusto in (("0", "O"), ("1", "I"), ("1", "L"), ("8", "B"), ("9", "G")):
        a = py.normalizza("AAAA-" + digitato * 4 + "-AAAA")
        b = py.normalizza("AAAA-" + giusto * 4 + "-AAAA")
        verifica(f"«{digitato}» digitato vale «{giusto}»", a == b, f"{a} vs {b}")

    # ── 2 · la porta dice ancora NO ai codici davvero sbagliati ────────────────
    # Il rischio della normalizzazione e' esagerare: se collassa troppo, apre a tutti.
    rng = random.Random(77)
    collisioni = 0
    campione = [seriale_finto(rng) for _ in range(4000)]
    impronte = {}
    for s in campione:
        n = py.normalizza(s)
        if n in impronte and impronte[n] != s:
            collisioni += 1
        impronte[n] = s
    verifica("4000 seriali diversi restano 4000 impronte diverse",
             collisioni == 0, f"collisioni trovate: {collisioni}")
    verifica("un codice completamente diverso viene respinto",
             py.normalizza("AAAA-BBBB-CCCC") != py.normalizza(vero))
    verifica("un codice troppo corto non diventa quello giusto",
             py.normalizza("GZSG-ZS62") != atteso)

    # ── 3 · l'ID della card NON passa dalla tabella ────────────────────────────
    # Se ci passasse, «SYS-00» diventerebbe «SYSOO» e la card non si troverebbe.
    js_id = normalizza_in_js(["SYS-00", "SYS-01", "SYS-02", "SYS-10"])["id"]
    verifica("l'ID resta SYS00 e non diventa SYSOO",
             js_id[0] == "SYS00", f"SYS-00 → {js_id[0]}")
    verifica("tutti gli ID restano riconoscibili",
             all(re.fullmatch(r"SYS\d{2}", v) for v in js_id), str(js_id))

    # ── 4 · Python e browser dicono la stessa cosa (il rischio dei gemelli) ────
    prove = campione[:300] + list(letture_sbagliate.values()) + [vero]
    js = normalizza_in_js(prove)["codice"]
    diverse = [(p, py.normalizza(p), j) for p, j in zip(prove, js) if py.normalizza(p) != j]
    verifica(f"le due implementazioni concordano su {len(prove)} casi",
             not diverse,
             "" if not diverse else f"prima divergenza: {diverse[0]}")

    # ── 5 · le card gia' online si aprono ancora ───────────────────────────────
    # Prova end-to-end sul dato pubblicato davvero, non su un esempio.
    interne = os.path.join(os.path.dirname(RADICE), "kiroshi-interno", "SIGILLO")
    provate = 0
    for nome in sorted(os.listdir(interne)) if os.path.isdir(interne) else []:
        if not re.fullmatch(r"card-\d{3}\.json", nome):
            continue
        interna = json.load(open(os.path.join(interne, nome), encoding="utf-8"))
        cid, ser = interna["card_id"], interna["seriale"]
        pubblico = os.path.join(RADICE, "docs", "anima", "verifica", "dati", f"{cid}.json")
        if not os.path.exists(pubblico):
            continue
        atteso_pub = json.load(open(pubblico, encoding="utf-8")).get("verifica_ingresso")
        # come lo digiterebbe uno che legge male tutte e tre le coppie
        maldestro = ser.lower().replace("g", "6").replace("z", "2").replace("s", "5")
        verifica(f"{cid}: il codice scritto giusto apre",
                 py.impronta("carta", cid, ser) == atteso_pub)
        verifica(f"{cid}: il codice letto male apre lo stesso",
                 py.impronta("carta", cid, maldestro) == atteso_pub)
        provate += 1
    verifica("almeno una card vera e' stata provata", provate > 0,
             f"card provate: {provate}")

    # ── esito ─────────────────────────────────────────────────────────────────
    larghezza = max(len(t) for t, _, _ in esiti)
    print("\n  IL TEST DELLE LETTERE AMBIGUE\n")
    for titolo, ok, dettaglio in esiti:
        print(f"  {'✓' if ok else '✗'}  {titolo.ljust(larghezza)}"
              + (f"   {dettaglio}" if dettaglio and not ok else ""))
    falliti = [t for t, ok, _ in esiti if not ok]
    print()
    if falliti:
        print(f"  ⛔ NON PASSA — {len(falliti)} controlli falliti su {len(esiti)}.")
        print("     @KIROSHI: SYS-02 non si conia finche' questo non e' verde.\n")
        return 1
    print(f"  🟢 PASSA — {len(esiti)} controlli, tutti verdi.")
    print("     @KIROSHI: il blocco §4 della scheda carta-02 e' chiuso.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
