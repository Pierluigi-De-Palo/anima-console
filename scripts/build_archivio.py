#!/usr/bin/env python3
"""Rigenera docs/data/archivio.js: UN archivio solo, dalle due sorgenti esistenti.

Perche' esiste questo script invece di un unico file di dati:
le due sorgenti hanno padroni diversi. I verdetti BRAINDANCE arrivano gia'
impaginati in docs/data/braindance.json, e il loro schema vive in
braindance/dati/SCHEMA.md -- casa di BRAINDANCE, non di questo repo. Le verifiche
KIROSHI nascono qui, un file per verdetto (docs/data/NNNN-slug.json).
Riscrivere la sorgente di BRAINDANCE la farebbe divergere dal suo generatore a
monte, e alla prossima pubblicazione il lavoro verrebbe sovrascritto in silenzio.

Quindi: le due sorgenti restano come sono, e qui si costruisce la vista unica.
Un formato, una lista, un contatore. Le pagine esistenti continuano a funzionare
sulle loro sorgenti; chi vuole l'archivio intero legge window.ARCHIVIO.

    python3 scripts/build_archivio.py

— creato da SQUELCH, 2026-08-01
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
OUT = os.path.join(DATA, "archivio.js")

# Coppie in conflitto: stessa affermazione verificata due volte dalle due squadre,
# con punteggi diversi. NON ne tolgo nessuna: quale valga e' una decisione
# editoriale, non tecnica, e nasconderne una senza che nessuno l'abbia deciso
# sarebbe peggio del conflitto. Le marco entrambe con `conflitto` -- cosi' ogni
# vista puo' mostrarle con un avviso, e il numero in home resta onesto.
CONFLITTI = [
    ("0002-social-contenuti-sensuali", "contenuti-sensuali-social"),
]

# Punteggio -> fascia colore. Stessa scala di comuni/STANDARD-VISUAL-v2 e di
# braindance/dati/SCHEMA.md: se cambia una, cambiano entrambe.
def colore_per(punteggio):
    if punteggio is None:
        return "grigio"
    if punteggio <= 40:
        return "rosso"
    if punteggio <= 70:
        return "giallo"
    return "verde"


def parole(testo):
    """Parole significative di un titolo, per accorgersi dei doppioni."""
    stop = {"il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da",
            "in", "con", "su", "per", "tra", "fra", "e", "che", "non", "e'", "è",
            "sono", "vero", "piu", "più", "dal", "del", "della", "sui", "sul"}
    t = re.sub(r"[^\w\s]", " ", (testo or "").lower())
    return {p for p in t.split() if len(p) > 2 and p not in stop}


def da_braindance(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    out = []
    for v in d.get("verdetti", []):
        out.append({
            "id": v.get("id"),
            "fonte": "braindance",
            "tipo": v.get("tipo") or "notizia",
            "titolo": v.get("titolo"),
            "esito": v.get("verdetto"),          # "Falso", "Parzialmente vero", …
            "punteggio": v.get("punteggio"),
            "colore": v.get("colore") or colore_per(v.get("punteggio")),
            "data": v.get("data"),
            "sintesi": v.get("note"),
            "scheda": v.get("scheda"),
            "fonti": v.get("fonti") or [],
        })
    return out


def da_kiroshi(paths):
    out = []
    for path in paths:
        nome = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            v = json.load(fh)
        out.append({
            "id": os.path.splitext(nome)[0],
            "fonte": "kiroshi",
            "tipo": "ditta",
            "titolo": v.get("titolo"),
            "esito": (v.get("etichetta") or "").capitalize(),   # "Affidabile", "Dubbio"
            "punteggio": v.get("punteggio"),
            "colore": colore_per(v.get("punteggio")),
            "data": v.get("data_verifica"),
            "sintesi": v.get("verdetto"),
            "scheda": None,                       # le verifiche KIROSHI non hanno una pagina propria
            "fonti": v.get("fonti") or [],
            # campi ricchi, solo KIROSHI: restano disponibili a chi li sa leggere
            "oggetto": v.get("oggetto"),
            "domanda": v.get("domanda"),
            "green_flags": v.get("green_flags") or [],
            "red_flags": v.get("red_flags") or [],
            "timeline": v.get("timeline") or [],
            "nota_sicurezza": v.get("nota_sicurezza"),
        })
    return out


def main():
    bd_path = os.path.join(DATA, "braindance.json")
    if not os.path.exists(bd_path):
        print("✗ manca docs/data/braindance.json")
        return 1

    voci = da_braindance(bd_path) + da_kiroshi(sorted(glob.glob(os.path.join(DATA, "[0-9]*.json"))))

    # regola editoriale, la stessa di build_db.py: un verdetto senza fonti non si pubblica
    senza_fonti = [v["id"] for v in voci if not v["fonti"]]
    voci = [v for v in voci if v["fonti"]]

    # conflitti dichiarati: le marco, non le tolgo
    per_id = {v["id"]: v for v in voci}
    dichiarati = []
    for a, b in CONFLITTI:
        if a in per_id and b in per_id:
            per_id[a]["conflitto"] = b
            per_id[b]["conflitto"] = a
            dichiarati.append((a, per_id[a]["punteggio"], b, per_id[b]["punteggio"]))

    # doppioni non ancora dichiarati: li segnalo, non li tolgo
    sospetti = []
    for i, a in enumerate(voci):
        for b in voci[i + 1:]:
            pa, pb = parole(a["titolo"]), parole(b["titolo"])
            if pa and pb and len(pa & pb) / len(pa | pb) >= 0.45:
                sospetti.append((a["id"], b["id"], a["punteggio"], b["punteggio"]))

    voci.sort(key=lambda v: v.get("data") or "", reverse=True)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.ARCHIVIO = ")
        json.dump({
            "totale": len(voci),
            "in_conflitto": sum(1 for v in voci if v.get("conflitto")),
            "per_fonte": {
                "braindance": sum(1 for v in voci if v["fonte"] == "braindance"),
                "kiroshi": sum(1 for v in voci if v["fonte"] == "kiroshi"),
            },
            "voci": voci,
        }, fh, ensure_ascii=False, indent=2)
        fh.write(";\n")

    print(f"✓ archivio.js — {len(voci)} voci "
          f"({sum(1 for v in voci if v['fonte']=='braindance')} braindance + "
          f"{sum(1 for v in voci if v['fonte']=='kiroshi')} kiroshi)")
    for a, pa, b, pb in dichiarati:
        print(f"  ⚠ CONFLITTO pubblico: {a} ({pa}) contro {b} ({pb}) — stessa affermazione,")
        print(f"    punteggi diversi, tutte e due online. Decide il Direttore quale vale.")
    for vid in senza_fonti:
        print(f"  ✗ scartato {vid}: nessuna fonte")
    for a, b, pa, pb in sospetti:
        print(f"  ⚠ possibile doppione NON dichiarato: {a} ({pa}) ~ {b} ({pb})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
