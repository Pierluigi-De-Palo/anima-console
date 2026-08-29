#!/usr/bin/env python3
"""
COSA FA — costruisce la sala di regia: legge i file veri del repo, mette in
chiaro i quattro numeri che possono stare in chiaro, cifra tutto il resto con la
passphrase del Direttore e incolla le due parti dentro docs/regia/index.html,
fra marcatori. Non tocca una riga fuori dai marcatori.

PERCHÉ ESISTE — la regia è servita da GitHub Pages: è pubblica per costruzione.
Un URL «segreto» non è un segreto, è un segreto nella cronologia di un telefono:
qui privato vuol dire cifrato. E i numeri della regia devono venire dai file —
una pagina di stato scritta a mano invecchia il giorno dopo e nessuno se ne
accorge (è la stessa lezione dell'etichetta `verifica` che non esisteva:
il manuale diceva una cosa, il repo un'altra, e nessuno dei due mentiva da solo).

FIN DOVE ARRIVA
  · Legge SOLO file locali: `squadra/SQUADRA.md`, `CLAUDE.md`, `docs/data/*.json`,
    `.claude/agents/*.md`. Niente rete, niente `gh`: le code delle issue non
    entrano nella regia (sarebbero diverse a ogni lancio e non sarebbero
    riproducibili). Se un dato non c'è nei file, resta un trattino.
  · Idempotenza: il salt è casuale alla PRIMA generazione e a ogni cambio di
    passphrase, poi viene RIUSATO dal payload già pubblicato. Anche i blocchi
    invariati vengono riusati tali e quali (lo script li ridecifra per saperlo).
    Così due lanci di fila non producono un secondo commit. Un blocco che cambia
    riceve sempre un IV nuovo: chiave+IV ripetuti su testi diversi è l'unico modo
    di rompere GCM, e non passa di qui. `--salt-nuovo` forza il ricambio totale.
  · Privacy: i percorsi interni (ROOT_CLODE, /RISERVATO/) vengono oscurati nel
    chiaro PRIMA di cifrare — la dottrina dice che in `docs/` non compaiono, e
    non si fa un'eccezione perché «tanto è cifrato». Quel che resta passa dalla
    guardia (`guardia_privacy.scandaglia`): un reperto grave ferma la build.
  · Restano visibili a chiunque, e non c'è modo di evitarlo: quanti blocchi ci
    sono e quanto pesano. I loro NOMI no, stanno dentro il cifrato.
  · La sicurezza è tutta nella passphrase. 210.000 iterazioni PBKDF2 rendono
    cara ogni prova, non impossibile: una passphrase corta resta una passphrase
    corta (sotto i 12 caratteri lo script rifiuta di lavorare).
  · Dipende da un solo file di casa, `scripts/aesgcm_puro.py` (AES-GCM in Python
    puro): niente `pip install` prima di poter pubblicare. Il resto è libreria
    standard — PBKDF2 lo fa hashlib.

USO — dal Mac, con la passphrase FUORI dalla riga di comando (la history è un log):
    export REGIA_PASSPHRASE='…'   && python3 scripts/build_regia.py
    oppure, senza export:            python3 scripts/build_regia.py
                                     (la prende da `squadra/chiavi.sh leggi regia`)
    python3 scripts/build_regia.py --controlla    # apre il payload pubblicato, non scrive
    python3 scripts/build_regia.py --salt-nuovo   # rigenera salt e tutti i blocchi
    python3 scripts/build_regia.py --rigido       # niente oscuramenti: al primo percorso interno si ferma

— creato da SQUELCH, 2026-08-29
"""
import argparse
import base64
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import aesgcm_puro                     # noqa: E402  (cifrario di casa, stessa cartella)
import guardia_privacy                 # noqa: E402  (la denylist è una sola, e vive lì)

ROOT = os.path.dirname(QUI)
PAGINA = os.path.join(ROOT, "docs", "regia", "index.html")
ITERAZIONI = 210_000                   # il motore in pagina rifiuta payload sotto 200.000
FRASE_MINIMA = 12

b64 = lambda b: base64.b64encode(b).decode("ascii")


# ── passphrase ───────────────────────────────────────────────────────────────
def passphrase() -> str:
    """Due sorgenti dichiarate, nessuna delle due è la riga di comando."""
    frase = os.environ.get("REGIA_PASSPHRASE", "")
    da = "REGIA_PASSPHRASE"
    if not frase:
        chiavi = os.path.join(ROOT, "squadra", "chiavi.sh")
        if os.path.exists(chiavi):
            r = subprocess.run(["bash", chiavi, "leggi", "regia"],
                               capture_output=True, text=True)
            if r.returncode == 0:
                frase, da = r.stdout.strip(), "chiavi.sh leggi regia"
    if not frase:
        raise SystemExit(
            "✗ nessuna passphrase.\n"
            "  export REGIA_PASSPHRASE='…'  (mai come argomento: finisce nella history)\n"
            "  oppure: bash squadra/chiavi.sh setta regia   e rilancia.")
    if len(frase) < FRASE_MINIMA:
        raise SystemExit(f"✗ passphrase di {len(frase)} caratteri: qui la sicurezza è tutta lì dentro, "
                         f"ne servono almeno {FRASE_MINIMA}.")
    print(f"  chiave presa da: {da}")
    return frase


def deriva(frase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", frase.encode("utf-8"), salt, ITERAZIONI, 32)


# ── lettura dei file veri ────────────────────────────────────────────────────
def pulisci(t: str) -> str:
    """Via il markup, resta la frase. I link diventano «testo (url)»."""
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", t)
    return re.sub(r"[*`]", "", t).strip()


def sezioni(md: str) -> dict:
    fuori, titolo, corpo = {}, "(testa)", []
    for riga in md.splitlines():
        if riga.startswith("## "):
            fuori[titolo] = "\n".join(corpo)
            titolo, corpo = riga[3:].strip(), []
        else:
            corpo.append(riga)
    fuori[titolo] = "\n".join(corpo)
    return fuori


def tabella(testo: str) -> list:
    """Righe di una tabella markdown → dizionari. Intestazione = prima riga utile."""
    righe = [r.strip() for r in testo.splitlines() if r.strip().startswith("|")]
    righe = [r for r in righe if not re.fullmatch(r"\|[\s\-:|]+\|", r)]
    if not righe:
        return []
    celle = lambda r: [pulisci(c) for c in r.strip("|").split("|")]
    testa = celle(righe[0])
    return [dict(zip(testa, celle(r))) for r in righe[1:] if len(celle(r)) == len(testa)]


def trova(nome: str, sez: dict, chiave_parziale: str) -> str:
    for k, v in sez.items():
        if chiave_parziale.lower() in k.lower():
            return v
    print(f"  ⚠ {nome}: sezione «{chiave_parziale}» non trovata — blocco vuoto")
    return ""


def dati_squadra() -> dict:
    md = open(os.path.join(ROOT, "squadra", "SQUADRA.md"), encoding="utf-8").read()
    sez = sezioni(md)

    roster = []
    for r in tabella(trova("SQUADRA.md", sez, "Caposquadra attivi")):
        persona = r.get("File-persona", "")
        roster.append({
            "nome": r.get("Caposquadra", ""),
            "dipartimento": r.get("Dipartimento", "").split("—")[0].strip(),
            "file": persona,
            # verificato, non dichiarato: il file-persona esiste davvero?
            "file_presente": bool(persona) and os.path.exists(os.path.join(ROOT, persona)),
            "modello": r.get("Modello", ""),
        })

    reg = trova("SQUADRA.md", sez, "Registro commesse")
    commesse = [{"n": r.get("#", ""), "data": r.get("Data", ""), "commessa": r.get("Commessa", ""),
                 "lotti": r.get("Lotti / caposquadra", ""), "esito": r.get("Esito", ""),
                 # stato dedotto da una regola sola: prima parola dell'esito
                 "stato": (r.get("Esito", "").split() or ["ignoto"])[0].rstrip(",.:")}
                for r in tabella(reg)]

    clienti = [{"sigla": r.get("Sigla", ""), "data": r.get("Data", ""),
                "traguardo": r.get("Traguardo", ""), "stato": r.get("Stato", ""),
                "prossimo": r.get("Prossimo passo", "")}
               for r in tabella(trova("SQUADRA.md", sez, "Registro commesse cliente"))]

    # Le segnalazioni si cercano in TUTTO il file, non in una sezione: al primo
    # collaudo stavano sotto un altro titolo e il blocco usciva vuoto in
    # silenzio — un dato che manca senza dirlo è peggio di un errore.
    segnalazioni = []
    if "Segnalazioni aperte" in md:
        for riga in md.split("Segnalazioni aperte", 1)[1].splitlines():
            if riga.startswith("- "):
                segnalazioni.append(pulisci(riga[2:]))
            elif riga.startswith("  ") and riga.strip() and segnalazioni:
                segnalazioni[-1] += " " + pulisci(riga)
            elif segnalazioni and not riga.strip():
                continue
    else:
        print("  ⚠ SQUADRA.md: nessuna «Segnalazioni aperte» — blocco vuoto")
    return {"roster": roster, "commesse": commesse, "clienti": clienti,
            "segnalazioni": segnalazioni}


def dati_verdetti() -> dict:
    files = sorted(glob.glob(os.path.join(ROOT, "docs", "data", "[0-9]*.json")))
    voci = []
    for p in files:
        with open(p, encoding="utf-8") as fh:
            v = json.load(fh)
        if not v.get("fonti"):          # stesso guardrail di build_db.py: senza fonti non conta
            continue
        voci.append({"id": re.match(r"\d+", os.path.basename(p)).group(0),
                     "punteggio": v.get("punteggio"), "data": v.get("data_verifica", "")})
    numeri = [int(v["id"]) for v in voci] or [0]
    punteggi = [v["punteggio"] for v in voci if isinstance(v["punteggio"], (int, float))]
    return {
        "totale": len(voci),
        "media": round(sum(punteggi) / len(punteggi)) if punteggi else None,
        "ultimo": max((v["data"] for v in voci), default=""),
        "prossimo": f"{max(numeri) + 1:04d}",
    }


def blocchi_noti() -> list:
    md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    for riga in md.splitlines():
        if riga.strip().startswith("**Blocchi noti:**"):
            coda = riga.split("**Blocchi noti:**", 1)[1]
            return [pulisci(x) for x in coda.split(" · ") if pulisci(x)]
    print("  ⚠ CLAUDE.md: riga «Blocchi noti» non trovata — blocco vuoto")
    return []


# ── guardie ──────────────────────────────────────────────────────────────────
SIGLA = re.compile(r"^C-\d{2,}$")
INTERNI = re.compile(r"ROOT_CLODE|/RISERVATO/|card-dati")


def guardia_clienti(clienti: list) -> None:
    """I clienti stanno nel repo per sigla e basta (CONVENZIONE-DUE-DRAGHI, §1).
    Qui non si oscura niente: se è comparso un nome, lo deve vedere un umano."""
    for c in clienti:
        if not SIGLA.match(c.get("sigla", "")):
            raise SystemExit(f"✗ registro clienti: «{c.get('sigla','')}» non è una sigla C-0N. "
                             "Un cliente entra nel repo per sigla: correggi SQUADRA.md.")
        testo = " ".join(str(v) for v in c.values())
        if re.search(guardia_privacy.EMAIL, testo):
            raise SystemExit(f"✗ registro clienti ({c['sigla']}): c'è un indirizzo email. "
                             "I recapiti stanno dal Direttore, non nel repo.")


def oscura(oggetto, contatore: dict, rigido: bool):
    """Percorsi interni fuori dal chiaro, ricorsivamente. In `docs/` non compaiono
    nemmeno dentro un cifrato: la regola non ha la clausola «tanto non si legge»."""
    if isinstance(oggetto, str):
        if INTERNI.search(oggetto):
            if rigido:
                raise SystemExit(f"✗ --rigido: percorso interno nel chiaro → «{oggetto[:70]}…»")
            contatore["n"] += 1
            return INTERNI.sub("‹interno›", oggetto)
        return oggetto
    if isinstance(oggetto, list):
        return [oscura(x, contatore, rigido) for x in oggetto]
    if isinstance(oggetto, dict):
        return {k: oscura(v, contatore, rigido) for k, v in oggetto.items()}
    return oggetto


def guardia_chiaro(blocchi: dict) -> None:
    testo = json.dumps(blocchi, ensure_ascii=False)
    reperti = guardia_privacy.scandaglia(testo, "payload della regia")
    gravi = [r for r in reperti if r.grave]
    avvisi = [r for r in reperti if not r.grave]
    for r in avvisi:
        print(f"  ⚠ {r.cosa}: …{r.estratto}…")
    if gravi:
        for r in gravi:
            print(f"  ⛔ {r.cosa}: …{r.estratto}…")
        raise SystemExit("✗ la guardia privacy ferma la build: quella roba non entra in docs/, "
                         "nemmeno cifrata.")


# ── payload ──────────────────────────────────────────────────────────────────
def serializza(nome: str, dati) -> bytes:
    """Chiaro di un blocco. Byte stabili: stesso contenuto → stessi byte, sempre."""
    return json.dumps({"nome": nome, "dati": dati}, ensure_ascii=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_esistente(html: str):
    m = re.search(r'<script id="regia-cifrato" type="application/json">(.*?)</script>',
                  html, re.S)
    if not m:
        return None
    try:
        p = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    return p if isinstance(p, dict) and p.get("v") == 1 else None


def costruisci_payload(blocchi: dict, frase: str, vecchio, salt_nuovo: bool) -> tuple:
    salt = os.urandom(16)
    riusa = {}
    if vecchio and not salt_nuovo:
        try:
            salt_vecchio = base64.b64decode(vecchio["salt"])
            chiave_vecchia = deriva(frase, salt_vecchio)
            for b in vecchio["blocchi"]:
                try:
                    chiaro = aesgcm_puro.decifra(chiave_vecchia, base64.b64decode(b["iv"]),
                                                 base64.b64decode(b["d"]))
                except ValueError:
                    continue        # passphrase cambiata o blocco alterato: si rifà tutto
                riusa[chiaro] = b
            if riusa:
                salt = salt_vecchio
        except (KeyError, ValueError, TypeError):
            pass                    # payload vecchio illeggibile: si riparte pulito

    chiave = deriva(frase, salt)
    fuori, nuovi = [], 0
    for nome, dati in blocchi.items():
        chiaro = serializza(nome, dati)
        if chiaro in riusa:
            fuori.append(riusa[chiaro])
            continue
        iv = os.urandom(12)         # blocco cambiato = IV nuovo, sempre
        fuori.append({"iv": b64(iv), "d": b64(aesgcm_puro.cifra(chiave, iv, chiaro))})
        nuovi += 1

    # Non si pubblica un lucchetto senza aver provato la chiave.
    for b, (nome, dati) in zip(fuori, blocchi.items()):
        if aesgcm_puro.decifra(chiave, base64.b64decode(b["iv"]),
                               base64.b64decode(b["d"])) != serializza(nome, dati):
            raise SystemExit("✗ il payload non si riapre: build fermata prima di scrivere.")

    return {"v": 1, "cifra": "AES-GCM-256", "kdf": "PBKDF2-SHA256",
            "iter": ITERAZIONI, "salt": b64(salt), "blocchi": fuori}, nuovi


# ── scrittura fra i marcatori ────────────────────────────────────────────────
def dentro(html: str, marca: str, corpo: str) -> str:
    a, b = f"<!--REGIA:{marca}:INIZIO-->", f"<!--REGIA:{marca}:FINE-->"
    i, j = html.find(a), html.find(b)
    if i < 0 or j < 0 or j < i:
        raise SystemExit(f"✗ docs/regia/index.html: marcatori {marca} assenti o invertiti. "
                         "Il generatore scrive solo fra i marcatori: non li rimette lui.")
    return html[:i + len(a)] + corpo + html[j:]


def come_json(id_tag: str, oggetto) -> str:
    # `<` fuori: un «</script>» dentro il JSON chiuderebbe il tag e la pagina.
    testo = json.dumps(oggetto, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    return f'\n<script id="{id_tag}" type="application/json">\n{testo}\n</script>\n'


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera la regia cifrata in docs/regia/index.html")
    ap.add_argument("--controlla", action="store_true", help="apre il payload pubblicato e non scrive niente")
    ap.add_argument("--salt-nuovo", action="store_true", help="salt e blocchi tutti rifatti")
    ap.add_argument("--rigido", action="store_true", help="nessun oscuramento: al primo percorso interno si ferma")
    args = ap.parse_args()

    aesgcm_puro.autoprova()
    if not os.path.exists(PAGINA):
        raise SystemExit(f"✗ manca {os.path.relpath(PAGINA, ROOT)}: il generatore riempie la pagina, "
                         "non la inventa.")
    html = open(PAGINA, encoding="utf-8").read()
    frase = passphrase()

    if args.controlla:
        p = payload_esistente(html)
        if not p:
            raise SystemExit("✗ nessun payload valido nella pagina.")
        chiave = deriva(frase, base64.b64decode(p["salt"]))
        nomi = []
        for b in p["blocchi"]:
            try:
                chiaro = aesgcm_puro.decifra(chiave, base64.b64decode(b["iv"]), base64.b64decode(b["d"]))
            except ValueError:
                raise SystemExit("✗ un blocco non si apre: passphrase sbagliata o payload manomesso.")
            nomi.append(json.loads(chiaro)["nome"])
        print(f"✓ payload apribile — {len(nomi)} blocchi: {', '.join(nomi)}")
        return 0

    # ── dati veri, nessun numero a mano
    sq = dati_squadra()
    vd = dati_verdetti()
    guardia_clienti(sq["clienti"])

    riservati = {
        "stato": {
            "blocchi_noti": blocchi_noti(),
            "commesse_totali": len(sq["commesse"]),
            "commesse_aperte": [c["n"] for c in sq["commesse"]
                                if c["stato"].lower() not in ("chiusa", "consegnata")],
            "clienti_attivi": len(sq["clienti"]),
            "prossimo_verdetto": vd["prossimo"],
        },
        "roster": sq["roster"],
        "commesse": sq["commesse"],
        "clienti": sq["clienti"],
        "segnalazioni": sq["segnalazioni"],
    }
    if not any(riservati["roster"] + riservati["commesse"]) and vd["totale"] == 0:
        raise SystemExit("✗ non ho letto nulla dai file: prima di cifrare il vuoto, mi fermo.")

    contatore = {"n": 0}
    riservati = oscura(riservati, contatore, args.rigido)
    if contatore["n"]:
        print(f"  · {contatore['n']} percorsi interni oscurati prima di cifrare")
    guardia_chiaro(riservati)

    # ── la data della regia esce dai dati, non dall'orologio: due lanci di fila
    #    nello stesso giorno o in giorni diversi danno lo stesso file.
    date = [vd["ultimo"]] + [c["data"] for c in sq["commesse"]] + [c["data"] for c in sq["clienti"]]
    pubblico = {
        "aggiornato": max((d for d in date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)), default=None),
        "verdetti": {"totale": vd["totale"], "media": vd["media"], "ultimo": vd["ultimo"] or None},
        "squadra": {"caposquadra": len(sq["roster"])},
        "generato_da": "scripts/build_regia.py",
    }

    payload, nuovi = costruisci_payload(riservati, frase, payload_esistente(html), args.salt_nuovo)

    fuori = dentro(html, "PUBBLICO", come_json("regia-pubblico", pubblico))
    fuori = dentro(fuori, "CIFRATO", come_json("regia-cifrato", payload))

    if fuori == html:
        print(f"= nessun cambiamento: {os.path.relpath(PAGINA, ROOT)} è già aggiornata "
              f"({len(payload['blocchi'])} blocchi, {vd['totale']} verdetti)")
        return 0
    with open(PAGINA, "w", encoding="utf-8") as fh:
        fh.write(fuori)
    print(f"✓ {os.path.relpath(PAGINA, ROOT)} — {len(payload['blocchi'])} blocchi cifrati "
          f"({nuovi} rifatti, {len(payload['blocchi']) - nuovi} riusati) · "
          f"pubblico: {vd['totale']} verdetti, media {vd['media']}, {len(sq['roster'])} caposquadra")
    return 0


if __name__ == "__main__":
    sys.exit(main())
