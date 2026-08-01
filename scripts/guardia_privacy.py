#!/usr/bin/env python3
"""Guardia: cerca dati che non devono stare in pubblico, prima che ci finiscano.

Nata dopo il 2026-08-01: una richiesta arrivata dal form conteneva "sto valutando
l'acquisizione" nel campo contesto, ed e' finita in una Issue pubblica. Chiunque,
azienda verificata compresa, poteva leggere le intenzioni del Direttore prima di
qualsiasi trattativa. Le Issue sono state cancellate; questo script serve a non
riscoprirlo la prossima volta a cose fatte.

Guarda due superfici:
  - docs/        cio che GitHub Pages pubblica (e che il repo pubblico serve due volte)
  - le Issue     la coda di lavoro, pubblica anch'essa

Due livelli, perche' non tutto e' uguale:
  BLOCCO      credenziali, recapiti, identificativi fiscali, percorsi interni.
              Non esistono ragioni buone perche' stiano li'. Esce con codice 1.
  ATTENZIONE  intenzioni private in prima persona ("sto valutando l'acquisizione").
              Servono occhi umani: una frase simile puo' essere legittima dentro un
              verdetto che parla dell'acquisizione fatta da altri. Non blocca.

    python3 scripts/guardia_privacy.py            # docs/ + Issue aperte
    python3 scripts/guardia_privacy.py --solo-docs # senza rete, buono come hook pre-push

Come hook pre-push (opzionale):
    ln -s ../../scripts/guardia_privacy.py .git/hooks/pre-push

— creato da SQUELCH, 2026-08-01
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# ── BLOCCO ────────────────────────────────────────────────────────────────────
# Roba che in una superficie pubblica non ha nessuna giustificazione.
BLOCCO = [
    ("token GitHub",      r"\bgh[pousr]_[A-Za-z0-9]{16,}"),
    ("chiave OpenAI/AI",  r"\bsk-[A-Za-z0-9_\-]{20,}"),
    ("chiave AWS",        r"\bAKIA[0-9A-Z]{16}\b"),
    ("segreto assegnato", r"(?i)\b(api[_-]?key|secret|password|passwd|bearer)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    ("IBAN",              r"\bIT\d{2}[A-Z]\d{10}[A-Z0-9]{12}\b"),
    ("codice fiscale",    r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b"),
    ("telefono italiano", r"(?<![\d/\-.])\+39[\s.]?\d{2,4}[\s.]?\d{5,8}(?![\d])"),
    ("percorso interno",  r"ROOT_CLODE|/RISERVATO/"),
]

# Email: bloccante, ma il dominio pubblico del progetto e' un recapito voluto.
EMAIL = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
EMAIL_AMMESSE = re.compile(r"@(cyberboomer\.io|anima\.solar|systema77\.com|example\.(com|org))$", re.I)

# ── ATTENZIONE ────────────────────────────────────────────────────────────────
# Intenzione privata in PRIMA PERSONA. Il vincolo del soggetto e' cio' che tiene
# bassi i falsi positivi: un verdetto che racconta l'acquisizione fatta da altri
# non scatta, una frase come "sto valutando l'acquisizione" si'.
SOGG = r"(?:sto|stiamo|vorrei|vorremmo|voglio|vogliamo|devo|dobbiamo|ho intenzione di|abbiamo intenzione di|sono in|siamo in)"
ATTENZIONE = [
    ("intenzione di acquisto/acquisizione",
     rf"(?i)\b{SOGG}\b[^.\n]{{0,60}}\b(acquisire|acquisizione|comprare|acquistare|rilevare|rilevamento)\b"),
    ("trattativa in corso",
     rf"(?i)\b{SOGG}\b[^.\n]{{0,60}}\b(trattativa|trattando|negozia\w*)\b"),
    ("materiale dichiarato riservato",
     r"(?i)\b(riservat[oa]|confidenzial[ei]|non divulgare|coperto da NDA|sotto NDA)\b"),
    ("cifra di spesa dichiarata",
     rf"(?i)\b{SOGG}\b[^.\n]{{0,40}}(spendere|investire|versare)\b[^.\n]{{0,20}}[\d.,]+\s*(euro|€|k€|mila)"),
]


class Reperto:
    def __init__(self, grave, dove, cosa, estratto):
        self.grave, self.dove, self.cosa, self.estratto = grave, dove, cosa, estratto


def _estratto(testo, m, largo=34):
    a, b = max(0, m.start() - largo), min(len(testo), m.end() + largo)
    return " ".join(testo[a:b].split())


def scandaglia(testo, dove):
    trovati = []
    for nome, pat in BLOCCO:
        for m in re.finditer(pat, testo):
            trovati.append(Reperto(True, dove, nome, _estratto(testo, m)))
    for m in re.finditer(EMAIL, testo):
        if not EMAIL_AMMESSE.search(m.group(0)):
            trovati.append(Reperto(True, dove, "indirizzo email", _estratto(testo, m)))
    for nome, pat in ATTENZIONE:
        for m in re.finditer(pat, testo):
            trovati.append(Reperto(False, dove, nome, _estratto(testo, m)))
    return trovati


def leggi_docs():
    out = []
    for base, _, files in os.walk(DOCS):
        for f in sorted(files):
            p = os.path.join(base, f)
            try:
                with open(p, encoding="utf-8") as fh:
                    out.append((os.path.relpath(p, ROOT), fh.read()))
            except (UnicodeDecodeError, OSError):
                continue
    return out


def leggi_issue():
    try:
        r = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "100",
             "--json", "number,title,body"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            print(f"  ⚠ Issue non lette ({r.stderr.strip()[:70]}) — controllati solo i docs/")
            return []
        return [(f"issue #{i['number']}", (i.get("title") or "") + "\n" + (i.get("body") or ""))
                for i in json.loads(r.stdout)]
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(f"  ⚠ Issue non lette ({type(e).__name__}) — controllati solo i docs/")
        return []


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--solo-docs", action="store_true", help="non interrogare GitHub")
    args = ap.parse_args()

    superfici = leggi_docs() + ([] if args.solo_docs else leggi_issue())

    reperti = []
    for dove, testo in superfici:
        reperti.extend(scandaglia(testo, dove))

    blocchi = [r for r in reperti if r.grave]
    avvisi = [r for r in reperti if not r.grave]

    print(f"  Guardia privacy — {len(superfici)} superfici pubbliche controllate")

    if blocchi:
        print(f"\n  ⛔ BLOCCO — {len(blocchi)} cose che non devono stare in pubblico:")
        for r in blocchi:
            print(f"     {r.dove}: {r.cosa}")
            print(f"       …{r.estratto}…")
    if avvisi:
        print(f"\n  ⚠ ATTENZIONE — {len(avvisi)} da guardare con occhi umani:")
        for r in avvisi:
            print(f"     {r.dove}: {r.cosa}")
            print(f"       …{r.estratto}…")
    if not reperti:
        print("  ✓ nessun dato privato trovato")

    if blocchi:
        print("\n  Non pubblicare finche' non sono usciti di li'.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
