#!/usr/bin/env python3
"""Rigenera docs/data/db.js dai file docs/data/NNNN-*.json.

Un verdetto = un file JSON. Aggiungi il file, lancia questo script, pusha.
    python3 scripts/build_db.py

— creato da KIROSHI//OR, 2026-07-19
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
OUT = os.path.join(DATA, "db.js")

RICHIESTI = ("titolo", "oggetto", "punteggio", "etichetta", "verdetto", "data_verifica")


def main() -> int:
    files = sorted(glob.glob(os.path.join(DATA, "[0-9]*.json")))
    if not files:
        print("Nessun verdetto trovato in docs/data/")
        return 1

    verdetti, problemi = [], []
    for path in files:
        nome = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as fh:
                v = json.load(fh)
        except json.JSONDecodeError as err:
            problemi.append(f"{nome}: JSON non valido — {err}")
            continue

        mancanti = [k for k in RICHIESTI if not v.get(k)]
        if mancanti:
            problemi.append(f"{nome}: campi mancanti — {', '.join(mancanti)}")
            continue

        if not v.get("fonti"):
            problemi.append(f"{nome}: nessuna fonte — regola editoriale violata")
            continue

        verdetti.append(v)

    if problemi:
        print("Verdetti scartati:")
        for p in problemi:
            print("  ✗", p)

    # più recenti in alto
    verdetti.sort(key=lambda v: v.get("data_verifica", ""), reverse=True)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.KIROSHI_DB = ")
        json.dump(verdetti, fh, ensure_ascii=False, indent=2)
        fh.write(";\n")

    media = round(sum(v["punteggio"] for v in verdetti) / len(verdetti)) if verdetti else 0
    print(f"✓ db.js rigenerato — {len(verdetti)} verdetti · punteggio medio {media}/100")
    return 0 if not problemi else 2


if __name__ == "__main__":
    sys.exit(main())
