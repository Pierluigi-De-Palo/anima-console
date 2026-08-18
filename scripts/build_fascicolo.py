#!/usr/bin/env python3
"""
COSA FA — impacchetta uno o più verdetti pubblicati (docs/data/NNNN-*.json) in UN
fascicolo sorgente: un documento pulito, citato, pronto da trascinare in
NotebookLM (o in qualunque strumento di rielaborazione divulgativa).

PERCHÉ ESISTE — NotebookLM consumer non ha API: il gesto del Direttore resta
manuale, ma deve durare 30 secondi su materiale già pronto, non mezz'ora di
copia-incolla artigianale. E la rielaborazione a valle (ECHO) deve poter risalire
di ogni fatto alla fonte: il fascicolo porta con sé URL e pesi delle fonti.

FIN DOVE ARRIVA — solo verdetti KIROSHI già pubblicati (stesso guardrail di
build_db.py: un verdetto senza fonti non entra). Non tocca le schede BRAINDANCE
(v2, quando serviranno) e non genera testo suo: impagina quello che c'è.

USO — python3 scripts/build_fascicolo.py <slug-tema> <NNNN> [NNNN ...]
      es. python3 scripts/build_fascicolo.py trappole-digitali 0001 0002
      → fascicoli/FASCICOLO-<slug-tema>-<AAAA-MM-GG>.md

— creato da SQUELCH su dispatch D.R.A.G.O., 2026-08-18
"""
import datetime
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
OUT_DIR = os.path.join(ROOT, "fascicoli")


def carica(nnnn: str) -> tuple[str, dict]:
    trovati = glob.glob(os.path.join(DATA, f"{nnnn}-*.json"))
    if len(trovati) != 1:
        raise SystemExit(f"✗ verdetto {nnnn}: attesi 1 file, trovati {len(trovati)}")
    with open(trovati[0], encoding="utf-8") as fh:
        v = json.load(fh)
    if not v.get("fonti"):
        raise SystemExit(f"✗ verdetto {nnnn}: senza fonti — non entra in un fascicolo")
    return os.path.basename(trovati[0]), v


def sezione(nome_file: str, v: dict) -> str:
    r = [f"## {v['titolo']} — {v['punteggio']}/100 · {v['etichetta']}", ""]
    r += [f"*Oggetto:* {v['oggetto']}  ", f"*Domanda:* {v.get('domanda', '—')}  ",
          f"*Verificato il:* {v.get('data_verifica', '—')} (fonte: `{nome_file}`)", ""]
    r += ["**Verdetto.** " + v["verdetto"], ""]
    if v.get("green_flags"):
        r += ["**A favore:**"] + [f"- {g}" for g in v["green_flags"]] + [""]
    if v.get("red_flags"):
        r += ["**Contro:**"] + [f"- {rf}" for rf in v["red_flags"]] + [""]
    if v.get("timeline"):
        r += ["**Cronologia:**"] + [f"- {t['data']} — {t['evento']}" for t in v["timeline"]] + [""]
    r += ["**Fonti (con peso 1-5):**"]
    r += [f"- [{f['titolo']}]({f['url']}) — {f.get('tipo','?')} · "
          f"autorevolezza {f.get('autorevolezza','?')}/5" for f in v["fonti"]]
    if v.get("nota_sicurezza"):
        r += ["", "> Nota di sicurezza: " + v["nota_sicurezza"]]
    return "\n".join(r)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    tema, numeri = sys.argv[1], sys.argv[2:]
    oggi = datetime.date.today().isoformat()
    voci = [carica(n) for n in numeri]

    testa = [
        f"# FASCICOLO SORGENTE · {tema} · {oggi}",
        "",
        "Materiale per rielaborazione divulgativa (NotebookLM o equivalente).",
        "Ogni fatto qui dentro risale a un verdetto pubblicato del Dipartimento",
        "Verità di SYSTEMA 77, con fonti linkate e pesate. Regola per chi",
        "rielabora: un numero che non sta in queste pagine resta un trattino.",
        "",
    ]
    corpo = "\n\n---\n\n".join(sezione(nf, v) for nf, v in voci)
    coda = ["", "---", "",
            f"Fascicolo generato da `scripts/build_fascicolo.py` — verdetti: "
            + " · ".join(numeri),
            f"— creato da SQUELCH su dispatch D.R.A.G.O., {oggi}"]

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"FASCICOLO-{tema}-{oggi}.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(testa) + corpo + "\n".join(coda) + "\n")
    print(f"✓ {os.path.relpath(out, ROOT)} — {len(voci)} verdetti impacchettati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
